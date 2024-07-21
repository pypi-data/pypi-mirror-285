import logging
from typing import Optional, List

from stable_baselines3.common.callbacks import EvalCallback
# noinspection PyUnresolvedReferences
from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv, VecEnvWrapper

from xumes.core.errors.running_ends_error import RunningEndsError
from xumes.modules.reinforcement_learning.i_trainer import ITrainer
from xumes.modules.reinforcement_learning.stable_baselines_trainer import StableBaselinesTrainer


class VecStableBaselinesTrainer(ITrainer):

    def __init__(self):
        self._vec_env = None
        self._trainers: List[StableBaselinesTrainer] = []
        self._envs = []
        self._first_trainer = None
        self.policy = None
        self._made = False

    def add_trainer(self, trainer: StableBaselinesTrainer):
        self._trainers.append(trainer)
        if self._first_trainer is None:
            self._first_trainer = trainer
        self._envs.append(lambda: trainer.env)

    @property
    def venv(self):
        return self._vec_env

    def make(self):
        # self._vec_env = SubprocVecEnv(self._envs, "fork")
        self._made = True
        self._vec_env = DummyVecEnv(self._envs)

    def train(self, save_path: str = None, eval_freq: int = 10000, logs_path: Optional[str] = None,
              logs_name: Optional[str] = None, previous_model_path: Optional[str] = None):
        if self._first_trainer is None:
            raise Exception("No training services added")

        if not self._made:
            self.make()

        policy_class = self._first_trainer.policy_class
        algorithm_type = self._first_trainer.algorithm_type
        total_timesteps = self._first_trainer.total_timesteps

        eval_callback = None
        if save_path:
            eval_callback = EvalCallback(self._vec_env, best_model_save_path=save_path,
                                         log_path=save_path, eval_freq=eval_freq,
                                         deterministic=True, render=False)

        self.make_algo(logs_path=logs_path)

        if previous_model_path:
            self.policy = self.policy.load(previous_model_path, env=self._vec_env, tensorboard_log=logs_path)

        self.policy = self.policy.learn(total_timesteps, callback=eval_callback, tb_log_name=logs_name)

    def save(self, path: str):
        self.policy.save(path)

    def free(self):
        if self._vec_env is not None:
            self._vec_env.close()
            self.policy = None

    def load(self, path: str):
        if self._first_trainer is None:
            raise Exception("No training services added")

        if not self._made:
            self.make()

        self.make_algo()

        self.policy = self.policy.load(path, env=self._vec_env)

    def make_algo(self, logs_path: Optional[str] = None):
        if self._first_trainer is None:
            raise Exception("No training services added")

        if not self._made:
            self.make()

        policy_class = self._first_trainer.policy_class
        algorithm_type = self._first_trainer.algorithm_type

        self.policy = policy_class(algorithm_type, self._vec_env, verbose=1, tensorboard_log=logs_path)

    def play(self, timesteps: int = None):

        class InferenceWrapper(VecEnvWrapper):
            def __init__(self, env):
                super(InferenceWrapper, self).__init__(env)
                self.training = False

            def reset(self):
                return self.venv.reset()

            def step_async(self, a):
                self.venv.step_async(a)

            def step_wait(self):
                return self.venv.step_wait()

        _envs = InferenceWrapper(self._vec_env)
        obs = _envs.reset()

        active_envs = [True] * len(self._envs)

        def step():
            nonlocal obs
            actions, _ = self.policy.predict(obs)
            for i in range(len(next(iter(obs.values())))):
                if active_envs[i]:
                    try:
                        single_action = actions[i]
                        single_obs, rewards, done, terminated, info = _envs.envs[i].step(single_action)

                        # Update obs
                        for key, val in single_obs.items():
                            obs[key][i] = val

                        if done or terminated:
                            _envs.envs[i].reset()
                    except RunningEndsError:
                        logging.info(f"Received stop signal for environment {i}. Closing environment.")
                        active_envs[i] = False
                        _envs.envs[i].close()

        if not timesteps:
            while any(active_envs):
                step()
        else:
            for _ in range(timesteps):
                step()

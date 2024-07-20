# vortex
A reinforcement learning algorithm framework

# 1. quick start


# 2. run tests
Run the following commands under project root directory (rlvortex/)

- test gym environments with *target environment* and *render* option.
  ```
  $ make -f runs/run_tests.mk [target_environment(-render)]
  ```
  - target_envrionment in [carpole, mountaincarc]
  - -render can not optional; if render is enabled, the test will run with GUI.
  - example (cartpole):
    - run cartpole headless test
        ```
        make -f runs/run_tests.mk cartpole
        ```
    - run cartpole with GUI test
        ```
        make -f runs/run_tests.mk cartpole-render
        ```
- test all gym environments headlessly
    ```
    make -f runs/run_tests.mk all-headless
    ```
- test all gym environments with GUI
    ```
    make -f runs/run_tests.mk all-render
    ```

# 3. benchmark
Run the following commands under project root directory (rlvortex/)


'''
$ make -f run_trainers.mk [target_environment(-render)]

'''
'''
$ make -f runs/run_trainers.mk [cartpole-vpg]
'''
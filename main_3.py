#! /usr/bin/env python
import os


def main():
    cloud_run_task_idx = os.getenv('CLOUD_RUN_TASK_INDEX')
    print(cloud_run_task_idx)


if __name__ == "__main__":
    main()

import json
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint


class TaskController(Node):

    def __init__(self):
        super().__init__('task_controller')

        self.arm_publisher = self.create_publisher(
            JointTrajectory,
            '/crane_plus_arm_controller/joint_trajectory',
            10
        )

        self.gripper_publisher = self.create_publisher(
            JointTrajectory,
            '/crane_plus_gripper_controller/joint_trajectory',
            10
        )

        ###### 動作計画を読み込む。コードを触らなくてもいいようにjson化」
        config_dir = Path(
            get_package_share_directory('pai_final_controller')
        ) / 'config'

        plan_path = config_dir / 'task_plan.json'
        self.plan = self.load_plan(str(plan_path))
        self.steps = self.plan['steps']
        self.step = 0

        self.get_logger().info(
            f"タスク開始: {self.plan.get('task_name', 'unknown')}"
        )

        # 1ステップごとに動作を実行する
        self.timer = self.create_timer(3.0, self.execute_task)

    def load_plan(self, file_path):
        """
        AIが生成したJSON形式の動作計画を読み込む。
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                plan = json.load(file)

            self.get_logger().info(
                f"動作計画を読み込みました: {file_path}"
            )
            return plan

        except FileNotFoundError:
            self.get_logger().error(
                f"動作計画ファイルが見つかりません: {file_path}"
            )
            raise

        except json.JSONDecodeError as error:
            self.get_logger().error(
                f"JSONの形式が不正です: {error}"
            )
            raise

    def execute_task(self):
        """
        AIが生成した動作計画を1ステップずつ実行する。
        """
        if self.step >= len(self.steps):
            self.get_logger().info('タスク完了')
            self.timer.cancel()
            return

        current_step = self.steps[self.step]
        action = current_step.get('action')
        step_name = current_step.get('name', f'Step {self.step + 1}')

        self.get_logger().info(
            f'Step {self.step + 1}: {step_name}'
        )

        if action == 'move_arm':
            positions = current_step.get('positions')

            if not self.is_valid_arm_positions(positions):
                self.get_logger().error(
                    'アーム関節角度の数が不正です。4個必要です。'
                )
                self.timer.cancel()
                return

            self.send_arm_command(positions)

        elif action == 'move_gripper':
            position = current_step.get('position')

            if position is None:
                self.get_logger().error(
                    'グリッパーのpositionが指定されていません。'
                )
                self.timer.cancel()
                return

            self.send_gripper_command(position)

        else:
            self.get_logger().error(
                f'未知の動作です。実行を中止します: {action}'
            )
            self.timer.cancel()
            return

        self.step += 1

    def is_valid_arm_positions(self, positions):
        """
        アームの関節角度が4個指定されているか確認する。
        """
        return (
            isinstance(positions, list)
            and len(positions) == 4
            and all(isinstance(value, (int, float)) for value in positions)
        )

    def send_arm_command(self, positions):
        message = JointTrajectory()

        message.joint_names = [
            'crane_plus_joint1',
            'crane_plus_joint2',
            'crane_plus_joint3',
            'crane_plus_joint4',
        ]

        point = JointTrajectoryPoint()
        point.positions = [float(value) for value in positions]
        point.time_from_start.sec = 2

        message.points = [point]
        self.arm_publisher.publish(message)

        self.get_logger().info(
            f'アーム指令を送信: {positions}'
        )

    def send_gripper_command(self, position):
        message = JointTrajectory()

        message.joint_names = [
            'crane_plus_joint_hand'
        ]

        point = JointTrajectoryPoint()
        point.positions = [float(position)]
        point.time_from_start.sec = 2

        message.points = [point]
        self.gripper_publisher.publish(message)

        self.get_logger().info(
            f'グリッパー指令を送信: {position}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = TaskController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('プログラムを終了します')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
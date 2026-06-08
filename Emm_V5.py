# 系统参数枚举
class SysParams():
    S_VER   = 0   # 获取软件版本和相应硬件版本
    S_RL    = 1   # 获取读取运行状态
    S_PID   = 2   # 获取PID参数
    S_VBUS  = 3   # 获取母线电压
    S_CPHA  = 5   # 获取电流相位
    S_ENCL  = 7   # 获取编码器校准后的偏移量
    S_TPOS  = 8   # 获取电机目标位置角度
    S_VEL   = 9   # 获取电机实时转速
    S_CPOS  = 10  # 获取电机实时位置角度
    S_PERR  = 11  # 获取电机位置误差角度
    S_FLAG  = 13  # 获取使能/复位/运转状态标志位
    S_Conf  = 14  # 获取驱动器配置
    S_State = 15  # 获取系统状态信息
    S_ORG   = 16  # 获取原点触发/丢失状态标志位


# 命令码映射（用于读取系统参数）
_READ_CMD_CODES = {
    SysParams.S_VER  : [0x1F],
    SysParams.S_RL   : [0x20],
    SysParams.S_PID  : [0x21],
    SysParams.S_VBUS : [0x24],
    SysParams.S_CPHA : [0x27],
    SysParams.S_ENCL : [0x31],
    SysParams.S_TPOS : [0x33],
    SysParams.S_VEL  : [0x35],
    SysParams.S_CPOS : [0x36],
    SysParams.S_PERR : [0x37],
    SysParams.S_FLAG : [0x3A],
    SysParams.S_ORG  : [0x3B],
    SysParams.S_Conf : [0x42, 0x6C],
    SysParams.S_State: [0x43, 0x7A],
}

# 校验字节常量
_CHECK_BYTE = 0x6B


class EmmV5:
    """Emm V5 驱动器控制类"""

    def __init__(self, uart):
        self.uart = uart
    # -----------------------------------------------------------------
    # 原始函数映射
    # -----------------------------------------------------------------
    def reset_curpos_to_zero(self, addr: int):
        """重置当前位置为零"""
        cmd = [addr, 0x0A, 0x6D, _CHECK_BYTE]
        self.uart.write(bytes(cmd))

    def reset_clog_pro(self, addr: int):
        """重置堵转保护"""
        cmd = [addr, 0x0E, 0x52, _CHECK_BYTE]
        self.uart.write(bytes(cmd))

    def read_sys_params(self, addr: int, s: SysParams):
        """读取系统参数"""
        codes = _READ_CMD_CODES.get(s)
        if not codes:
            raise ValueError(f"未支持的系统参数: {s}")

        cmd = [addr]
        cmd.extend(codes)
        cmd.append(_CHECK_BYTE)
        self.uart.write(bytes(cmd))

    def modify_ctrl_mode(self, addr: int, svF: int, ctrl_mode: int):
        """
        修改控制/步进电机模式
        :param svF: 是否存储标志 0不存储 1存储
        :param ctrl_mode: 控制模式 (0关闭,1脉冲,2步进,3环形位置/位置控制)
        """
        cmd = [addr, 0x46, 0x69, svF, ctrl_mode, _CHECK_BYTE]
        self.uart.write(bytes(cmd))

    def en_control(self, addr: int, state: int, snF: int):
        """
        使能信号控制
        :param state: 1使能 0关闭
        :param snF: 同步控制标志 0不同步 1同步
        """
        cmd = [addr, 0xF3, 0xAB, state, snF, _CHECK_BYTE]
        self.uart.write(bytes(cmd))

    def vel_control(self, addr: int, dir_: int, vel: int, acc: int, snF: int):
        """
        速度模式控制
        :param dir_: 方向 0=CW 1=CCW
        :param vel: 速度 0~5000 RPM
        :param acc: 加速度 0~255 (0直达)
        :param snF: 同步控制标志
        """
        cmd = [
            addr,
            0xF6,
            dir_,
            (vel >> 8) & 0xFF,
            vel & 0xFF,
            acc,
            snF,
            _CHECK_BYTE
        ]
        self.uart.write(bytes(cmd))

    def pos_control(self, addr: int, dir_: int, vel: int, acc: int,
                    clk: int, raF: int, snF: int):
        """
        位置模式控制
        :param dir_: 方向 0=CW 1=CCW
        :param vel: 速度 0~5000 RPM
        :param acc: 加速度 0~255
        :param clk: 脉冲数 0~2^32-1
        :param raF: 相对/绝对标志 0相对 1绝对
        :param snF: 同步控制标志
        """
        cmd = [
            addr,
            0xFD,
            dir_,
            (vel >> 8) & 0xFF,
            vel & 0xFF,
            acc,
            (clk >> 24) & 0xFF,
            (clk >> 16) & 0xFF,
            (clk >> 8) & 0xFF,
            clk & 0xFF,
            raF,
            snF,
            _CHECK_BYTE
        ]
        self.uart.write(bytes(cmd))

    def stop_now(self, addr: int, snF: int):
        """立即停止电机运行（所有模式通用）"""
        cmd = [addr, 0xFE, 0x98, snF, _CHECK_BYTE]
        self.uart.write(bytes(cmd))

    def synchronous_motion(self, addr: int):
        """驱动器同步开始运动"""
        cmd = [addr, 0xFF, 0x66, _CHECK_BYTE]
        self.uart.write(bytes(cmd))

    def origin_set_o(self, addr: int, svF: int):
        """
        设置原点位置
        :param svF: 是否存储标志 0不存储 1存储
        """
        cmd = [addr, 0x93, 0x88, svF, _CHECK_BYTE]
        self.uart.write(bytes(cmd))

    def origin_modify_params(self, addr: int, svF: int, o_mode: int,
                             o_dir: int, o_vel: int, o_tm: int,
                             sl_vel: int, sl_ma: int, sl_ms: int, potF: int):
        """
        修改原点参数
        :param svF:      是否存储标志
        :param o_mode:   原点模式 0环形触发,1环形返回,2环形碰撞,3环形位置返回
        :param o_dir:    原点方向 0=CW 1=CCW
        :param o_vel:    原点速度 RPM
        :param o_tm:     原点超时时间 毫秒
        :param sl_vel:   原点位置碰撞转速 RPM
        :param sl_ma:    原点位置碰撞电流 mA
        :param sl_ms:    原点位置碰撞时间 ms
        :param potF:     位置触发自动原点 0不使能 1使能
        """
        cmd = [
            addr,
            0x4C, 0xAE,
            svF,
            o_mode,
            o_dir,
            (o_vel >> 8) & 0xFF,
            o_vel & 0xFF,
            (o_tm >> 24) & 0xFF,
            (o_tm >> 16) & 0xFF,
            (o_tm >> 8) & 0xFF,
            o_tm & 0xFF,
            (sl_vel >> 8) & 0xFF,
            sl_vel & 0xFF,
            (sl_ma >> 8) & 0xFF,
            sl_ma & 0xFF,
            (sl_ms >> 8) & 0xFF,
            sl_ms & 0xFF,
            potF,
            _CHECK_BYTE
        ]
        self.uart.write(bytes(cmd))

    def origin_trigger_return(self, addr: int, o_mode: int, snF: int):
        """
        触发原点返回
        :param o_mode: 原点模式 (0~3)
        :param snF: 同步控制标志
        """
        cmd = [addr, 0x9A, o_mode, snF, _CHECK_BYTE]
        self.uart.write(bytes(cmd))

    def origin_interrupt(self, addr: int):
        """强制中断退出原点"""
        cmd = [addr, 0x9C, 0x48, _CHECK_BYTE]
        self.uart.write(bytes(cmd))







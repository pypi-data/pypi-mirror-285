INF: float = 1e10  # 100_0000_0000


class Param:
    LogToConsole = "LogToConsole"
    TimeLimit = "TimeLimit"
    MIPGap = "MIPGap"  # mip gap limit, gap = (bestbound - bestsol) / bestbound
    MIPFocus = "MIPFocus"
    NodeLimit = "NodeLimit"  # mip node search number limit
    PoolSolutions = "PoolSolutions"  # mip pool solutions number limit

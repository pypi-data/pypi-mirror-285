def print_ply(ply: int):
  idx = ply // 2 + 1
  return f"{idx}." if ply % 2 == 0 else f"{idx}..."

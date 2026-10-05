#!/usr/bin/env python3
"""accordion - 终端手风琴纸牌接龙 (Accordion Solitaire)。

规则: 52 张牌依次发成一排。从左往右, 每一张牌可以放到左边
第 1 或第 3 位置上的牌上, 条件是两张牌花色相同或点数相同。
被覆盖的牌形成牌堆。目标: 最终只剩一个牌堆即获胜。
"""
import argparse
import random
import secrets
import sys

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def new_deck(rng):
    deck = [(r, s) for s in SUITS for r in RANKS]
    rng.shuffle(deck)
    return deck


def card_name(card):
    r, s = card
    return f"{s}{r}"


def can_move(top, dest):
    """top 能否放到 dest 上: 花色相同或点数相同。"""
    return top[0] == dest[0] or top[1] == dest[1]


class Game:
    def __init__(self, seed=None):
        rng = random.Random(seed) if seed is not None else secrets.SystemRandom()
        self.piles = [[c] for c in new_deck(rng)]
        self.moves = 0

    def top(self, i):
        return self.piles[i][-1] if self.piles[i] else None

    def legal_dests(self, i):
        """牌堆 i 可移动到的目标位置列表 (1 左或 3 左, 且可叠放)。"""
        dests = []
        for d in (1, 3):
            j = i - d
            if j >= 0 and can_move(self.top(i), self.top(j)):
                dests.append(j)
        return dests

    def move(self, i, j):
        """把牌堆 i 整体放到牌堆 j 上。成功返回 True。"""
        if j not in self.legal_dests(i):
            return False
        self.piles[j].extend(self.piles[i])
        del self.piles[i]
        self.moves += 1
        return True

    def any_move(self):
        for i in range(len(self.piles)):
            if self.legal_dests(i):
                return True
        return False

    def won(self):
        return len(self.piles) == 1


def render(g):
    parts = []
    for i, p in enumerate(g.piles):
        label = card_name(p[-1]) + (f"×{len(p)}" if len(p) > 1 else "")
        parts.append(f"[{i}:{label}]")
    print(" ".join(parts))
    print(f"牌堆数: {len(g.piles)}  步数: {g.moves}")


def auto_play(seed=None, prefer3=True, verbose=False):
    g = Game(seed)
    guard = 0
    while not g.won() and g.any_move() and guard < 100000:
        guard += 1
        moved = False
        order = range(len(g.piles) - 1, -1, -1)
        # 优先找 3-left 跳跃, 否则 1-left
        for dist in ((3, 1) if prefer3 else (1, 3)):
            for i in order:
                if i - dist >= 0 and (i - dist) in g.legal_dests(i):
                    g.move(i, i - dist)
                    moved = True
                    break
            if moved:
                break
    if verbose:
        render(g)
    return g


def play_interactive(seed):
    if not sys.stdin.isatty():
        print("error: 交互模式需要终端, 请用 --auto 自动游玩。", file=sys.stderr)
        sys.exit(2)
    g = Game(seed)
    print("手风琴纸牌: 把每张牌放到左边第 1 或第 3 张上 (花色或点数相同)。")
    print("命令: <i> <j>  (把牌堆 i 放到牌堆 j 上), u 撤销? (无), q 退出")
    print("目标: 只剩 1 个牌堆。")
    while True:
        render(g)
        if g.won():
            print(f"🎉 获胜! 共用 {g.moves} 步。")
            return
        if not g.any_move():
            print(f"无可用移动, 剩余 {len(g.piles)} 堆。游戏结束。")
            return
        try:
            text = input("走子 (i j / q): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            return
        if text.lower() in ("q", "quit", "退出"):
            print("已退出。")
            return
        parts = text.split()
        if len(parts) != 2 or not all(p.lstrip("-").isdigit() for p in parts):
            print("用法: <i> <j>, 例如 `4 1`。")
            continue
        i, j = int(parts[0]), int(parts[1])
        if not (0 <= i < len(g.piles) and 0 <= j < len(g.piles)):
            print(f"位置超出范围 (0..{len(g.piles) - 1})。")
            continue
        if g.move(i, j):
            print(f"已把牌堆 {i} 放到牌堆 {j} 上。")
        else:
            print("非法移动: 目标必须是左边第 1 或第 3 张, 且花色或点数相同。")


def main(argv=None):
    ap = argparse.ArgumentParser(description="手风琴纸牌接龙 (Accordion Solitaire)")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument("--auto", action="store_true", help="自动游玩 (机器人)")
    ap.add_argument("--no-prefer3", action="store_true", help="机器人不优先 3-left 跳跃")
    ap.add_argument("-v", "--verbose", action="store_true", help="自动游玩后打印终局")
    args = ap.parse_args(argv)
    if args.auto:
        g = auto_play(args.seed, prefer3=not args.no_prefer3, verbose=args.verbose)
        print(f"自动游玩结束: {'获胜' if g.won() else '失败'}, "
              f"剩余 {len(g.piles)} 堆, 步数 {g.moves}。")
    else:
        play_interactive(args.seed)


if __name__ == "__main__":
    raise SystemExit(main())

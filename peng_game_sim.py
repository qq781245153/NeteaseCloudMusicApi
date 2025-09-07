import random
import argparse
from collections import Counter


NUM_TYPES = 9  # 卡牌类型数
POOL_SIZE = 54  # 卡池上限
INITIAL_FIELD_SIZE = 9  # 初始发到场上的卡数


def simulate_one_game(random_gen: random.Random) -> int:
    """
    模拟一局游戏，根据题述规则返回本局碰次数。

    规则解读与实现要点：
    - 卡牌类型共 9 种，均匀随机。
    - 初始发 9 张牌到场上；若 9 张全不同，直接结束，碰数为 0。
    - 选择许愿类型（对称性下固定为 0 即可）。
    - 许愿池：场上每出现一张许愿卡（类型==许愿类型）时 +1。
    - 当有任意类型存在一对（计数>=2）时，可进行一次“碰”：消除 2 张同类卡，碰次+1；随后从卡池发 1 张牌到场上（若卡池有剩余）。
    - 使用许愿池：当场上没有任何可配对的牌且许愿池>0时，可再发 1 张牌到场上。
        * 若发出的牌是许愿类型：按题意“许愿池不需要-1”且该牌出现令许愿池+1，故净变化为 +1。
        * 若不是许愿类型：许愿池 -1。
    - 游戏结束：当场上无可配对且许愿池==0（或卡池无牌可发且无可配对）时结束。
    - 卡池上限为 54，用尽后不再发牌；仍可继续消除已在场上的成对牌。
    """

    wish_type = 0  # 对称性：任一固定类型等价

    # 初始发牌
    field_counts = [0] * NUM_TYPES
    for _ in range(INITIAL_FIELD_SIZE):
        t = random_gen.randrange(NUM_TYPES)
        field_counts[t] += 1

    # 规则 7：若初始 9 张全部不同，直接 0 碰结束
    if sum(1 for c in field_counts if c > 0) == INITIAL_FIELD_SIZE:
        return 0

    # 初始许愿池：场上每出现一张许愿卡 +1
    wish_pool = field_counts[wish_type]

    collisions = 0
    cards_remaining = POOL_SIZE - INITIAL_FIELD_SIZE

    while True:
        # 先尽可能消除场上的对（每次消除后发 1 张牌，若有剩余）
        paired_types = [i for i, c in enumerate(field_counts) if c >= 2]
        if paired_types:
            # 随机选择一个可配类型消除（顺序不影响分布的对称性）
            t_pair = paired_types[random_gen.randrange(len(paired_types))]
            field_counts[t_pair] -= 2
            collisions += 1
            # 消除后从卡池发 1 张（若可发）
            if cards_remaining > 0:
                t_new = random_gen.randrange(NUM_TYPES)
                field_counts[t_new] += 1
                if t_new == wish_type:
                    wish_pool += 1
                cards_remaining -= 1
            # 继续循环，看看是否还有可配
            continue

        # 没有可配对的牌时，尝试使用许愿池发一张
        if wish_pool > 0 and cards_remaining > 0:
            t_new = random_gen.randrange(NUM_TYPES)
            field_counts[t_new] += 1
            if t_new == wish_type:
                # 不扣费 + 出现许愿卡 +1
                wish_pool += 1
            else:
                wish_pool -= 1
            cards_remaining -= 1
            # 发完后继续循环，可能产生新的配对
            continue

        # 若无法继续（无可配，且许愿池==0 或 卡池无牌可发），游戏结束
        break

    return collisions


def run_simulation(num_trials: int, seed: int | None = None) -> Counter:
    rng = random.Random(seed)
    result_counter: Counter = Counter()
    for _ in range(num_trials):
        k = simulate_one_game(rng)
        result_counter[k] += 1
    return result_counter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=200000, help="模拟次数")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    args = parser.parse_args()

    counter = run_simulation(args.trials, args.seed)
    total = sum(counter.values())

    # 输出 0..14 碰 的概率；>14 归入 others
    max_k = 14
    others = 0
    for k, v in counter.items():
        if k > max_k:
            others += v

    print("Trials:", total)
    for k in range(0, max_k + 1):
        p = counter.get(k, 0) / total
        print(f"{k}\t{p:.6f}")
    if others:
        print(f">{max_k}\t{others / total:.6f}")


if __name__ == "__main__":
    main()


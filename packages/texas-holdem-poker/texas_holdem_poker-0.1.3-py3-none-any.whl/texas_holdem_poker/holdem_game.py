"""
    A command-line-interactive texas holdem poker game

    how to play:
        from texas_holdem_poker import HoldemGame

        HoldemGame.run()
"""
import time
import random

from typing import List, Dict

from .poker_ai import HoldemAI, HoldemScore, HandRankCheck, HoldemAction
from .dealer import Dealer


class PlayerProperty:
    def __init__(self, money=1000, ai: HoldemAI = None):
        self.money = money
        self.ai = ai


class HoldemGame:
    PLAYER_NUMS = 6
    BOTTOM = 10
    INITIAL_MONEY = 1000
    HUMAN_PLAYER_INDEX = 0

    def __init__(self):
        self.properties = {}
        for i in range(self.PLAYER_NUMS):
            self.properties[i] = PlayerProperty(money=self.INITIAL_MONEY, ai=HoldemAI())

        self.total_defeat = 0

    def show_money(self):
        for i in range(self.PLAYER_NUMS):
            if i == self.HUMAN_PLAYER_INDEX:
                print("Your money: %s" % self.properties[i].money)
            else:
                print("Player%s money: %s" % (i, self.properties[i].money))

    @staticmethod
    def input_bet():
        while True:
            bet = input()
            try:
                bet = int(bet.strip())
                break
            except ValueError:
                print("illegal input, please type integer! (tips: negative value like -1 represent fold)")

        if bet < 0:  # fold
            return -1

        return bet

    def run(self):
        print("""
            Texas Holdem Poker Simulator
        """)
        while True:  # start a new round
            # property check
            for player in range(self.PLAYER_NUMS):
                if self.properties[player].money <= 0:
                    if player == self.HUMAN_PLAYER_INDEX:
                        print("You lose all your money!")
                        print("Totally defeat %s AIs!" % self.total_defeat)
                        if self.total_defeat > 5:
                            print("Well played!")
                        elif self.total_defeat > 10:
                            print("You are really good at this!")
                        elif self.total_defeat > 20:
                            print("You are pro!")
                        elif self.total_defeat > 50:
                            print("OMG! How did you make it?")
                        print("try again? Y/N")
                        if input().lower().strip() not in ["y", "1", "yes", "ok", "restart"]:
                            exit()
                        else:
                            print("""
                                Restart game!
                            """)
                            self.__init__()
                    else:  # other player lose
                        self.total_defeat += 1
                        print("Player%s lost all his money!" % player)
                        time.sleep(1)
                        del self.properties[player].ai
                        print("Player%s is eliminated!" % player)
                        time.sleep(2)
                        self.properties[player].ai = HoldemAI()
                        self.properties[player].money = self.INITIAL_MONEY
                        print("A new AI has come!")
                        print("You have already defeat %s AI!" % self.total_defeat)

            time.sleep(1)
            print("\n")
            self.show_money()

            board = Dealer.deal(self.PLAYER_NUMS)

            pool = 0
            player_bets: dict = {}  # chips player has already bet
            remain_rounds = 4
            remain_players = list(range(self.PLAYER_NUMS))

            community_cards = board.get(board.SLOT_PUBLIC)

            while True:  # every round, pre-flop -> flop -> turn -> river -> showdown
                pool_last_round = pool
                flag_horse_racing = (
                        (len([1 for player in remain_players if self.properties[player].money > 0]) <= 1)
                        and (len(remain_players) > 1) and remain_rounds > 0
                )  # all remaining players bet their all money
                if not flag_horse_racing:
                    print("\nRound: %s" % (4 - remain_rounds))
                else:
                    print("Horse Racing!")
                    if remain_rounds > 1:
                        print("community: %s" % community_cards[0:(6 - remain_rounds)])
                        time.sleep(1)
                    remain_rounds -= 1
                    if remain_rounds != 0:
                        continue

                if (
                        remain_rounds <= 0 or
                        len([1 for player in remain_players if self.properties[player].money > 0]) <= 1
                ):  # game finish
                    # display leaderboard
                    print("community: %s" % community_cards)
                    print("your hands: %s, %s" % (
                        board.get(self.HUMAN_PLAYER_INDEX), HandRankCheck.check(
                            board.get_construction(self.HUMAN_PLAYER_INDEX)
                        )
                    ))
                    for player in remain_players:
                        if player != self.HUMAN_PLAYER_INDEX:
                            print("AI%s hands: %s, %s" % (
                                player, board.get(player), HandRankCheck.check(board.get_construction(player))
                            ))

                    # decide who wins
                    score_status: Dict[HoldemScore, List] = {}

                    for player in remain_players:
                        score = HandRankCheck.check(board.get_construction(player))
                        score_status[score] = score_status.get(score, [])
                        score_status[score].append(player)

                    winner_order: List[List] = [
                        winner_group for score, winner_group in
                        sorted(score_status.items(), key=lambda x: x[0], reverse=True)
                    ]

                    # divide prize pool
                    human_player_earned = -player_bets.get(self.HUMAN_PLAYER_INDEX, 0)
                    for winner_group in winner_order:
                        # announce first winner group
                        if winner_group == winner_order[0]:
                            for winner in winner_group:
                                if winner == self.HUMAN_PLAYER_INDEX:
                                    print("you win!")
                                else:
                                    print("AI%s win!" % winner)

                        # division algorithm
                        winners_by_bet_ascend = sorted(winner_group, key=lambda x: player_bets.get(x))

                        for winner_idx in range(len(winners_by_bet_ascend)):
                            winner = winners_by_bet_ascend[winner_idx]
                            chips_base = player_bets.get(winner)

                            pot = 0
                            for player in player_bets:
                                chips_to_transfer = (
                                    chips_base
                                    if player_bets.get(player, 0) > chips_base else
                                    player_bets.get(player, 0)
                                )
                                player_bets[player] = player_bets.get(player, 0) - chips_to_transfer
                                pot += chips_to_transfer

                            chips_ought_to_win = int(round(pot / len(winners_by_bet_ascend[winner_idx::])))

                            for winner_to_give in winners_by_bet_ascend[winner_idx::]:
                                self.properties[winner_to_give].money += chips_ought_to_win
                                if winner_to_give == self.HUMAN_PLAYER_INDEX:
                                    human_player_earned += chips_ought_to_win

                    # tooltip of earning
                    if human_player_earned > 0:
                        print("you have earned %s!" % human_player_earned)
                        if human_player_earned > 1000 and random.random() > 0.3:
                            print("What a hot 'pot'!")
                    elif human_player_earned < 0:
                        print("you have lost %s!" % abs(human_player_earned))

                    print("continue?")
                    if input().lower().strip() in ["no", "n", "0"]:
                        exit()
                    print("\n")
                    break

                if remain_rounds != 4:
                    print("community: %s" % community_cards[0:(6 - remain_rounds)])

                bottom = self.BOTTOM if remain_rounds == 4 else 0  # you can check after pre-flop
                raised_player = None
                chips_on_board = {}
                raising_round = 0
                while True:
                    raising_round += 1  # at most 3 chance to raise
                    if self.HUMAN_PLAYER_INDEX in remain_players and self.properties[self.HUMAN_PLAYER_INDEX].money > 0:
                        if raised_player == self.HUMAN_PLAYER_INDEX:  # end raising
                            break
                        # HUMAN PLAYER ACTION

                        print("now your turn, your cards:", board.get(0))
                        print("remaining money: %s, already bet: %s" % (
                            self.properties[self.HUMAN_PLAYER_INDEX].money, player_bets.get(self.HUMAN_PLAYER_INDEX, 0)
                        ))
                        print("input your bet:")
                        bet = self.input_bet()
                        if bet < 0:
                            print("you fold.")
                            remain_players.remove(self.HUMAN_PLAYER_INDEX)
                        else:
                            if bet < bottom:
                                bet = bottom

                            if bet > bottom and raising_round > 3:
                                print("reach the limit of raising (at most 3)!")
                                bet = bottom

                            chips_on_board[self.HUMAN_PLAYER_INDEX] = chips_on_board.get(self.HUMAN_PLAYER_INDEX, [])
                            diff = bet - sum(chips_on_board[self.HUMAN_PLAYER_INDEX])

                            if diff >= self.properties[self.HUMAN_PLAYER_INDEX].money:
                                print("YOU: ALL IN!")
                                diff = self.properties[self.HUMAN_PLAYER_INDEX].money

                            chips_on_board[self.HUMAN_PLAYER_INDEX].append(diff)

                            pool += diff
                            self.properties[self.HUMAN_PLAYER_INDEX].money -= diff
                            player_bets[self.HUMAN_PLAYER_INDEX] = player_bets.get(self.HUMAN_PLAYER_INDEX, 0) + diff

                            chips = sum(chips_on_board.get(self.HUMAN_PLAYER_INDEX, []))

                            if chips > bottom:
                                print("you raise bet to %s" % chips)
                                raised_player = self.HUMAN_PLAYER_INDEX
                                bottom = chips
                            else:
                                print("you %s, bet %s" % (("check" if bottom == 0 else "call"), min(chips, bottom)))

                    # AI PLAYER ACTION
                    folded_players = []
                    for player in remain_players:
                        if player != self.HUMAN_PLAYER_INDEX:
                            if raised_player == player:  # end raising
                                raised_player = None
                                break
                            if self.properties[player].money <= 0:
                                continue
                            decision = self.properties[player].ai.decide(**{
                                "bottom": bottom,
                                "bet_pool": pool_last_round,
                                "sunk_cost": player_bets.get(player, 0),
                                "remaining_chips": self.properties[player].money,

                                "other_player_count": self.PLAYER_NUMS - 1,
                                "remain_other_player_count": len(remain_players) - 1,
                                "unmoved_player_count": len([other for other in remain_players if other > player]),
                                "remain_rounds": remain_rounds,

                                "hand_cards": board.get(player),
                                "priori_cards": community_cards[0:(6 - remain_rounds)],

                                "simulate_times": 1500
                            })
                            if decision.action == HoldemAction.FOLD:
                                print("AI%s fold." % player)
                                folded_players.append(player)
                            else:
                                # if reach the limit of raising
                                if decision.action == HoldemAction.RAISE and raising_round > 3:
                                    decision.action = HoldemAction.CALL
                                    decision.bet = bottom

                                if decision.bet >= self.properties[player].money + sum(chips_on_board.get(player, [])):
                                    print("AI%s: ALL IN!" % player)

                                if decision.action == HoldemAction.RAISE:
                                    print("AI%s raise bet to %s" % (player, decision.bet))
                                    raised_player = player
                                    bottom = decision.bet
                                elif decision.action == HoldemAction.CALL:
                                    print(
                                        "AI%s %s, bet %s" % (
                                            player, ("check" if decision.bet == 0 else "call"),
                                            min(
                                                decision.bet,
                                                self.properties[player].money + sum(chips_on_board.get(player, []))
                                            )
                                        )
                                    )

                                chips_on_board[player] = chips_on_board.get(player, [])

                                diff = bottom - sum(chips_on_board.get(player, []))
                                if diff > self.properties[player].money:  # call but have no enough money
                                    diff = self.properties[player].money

                                chips_on_board[player].append(diff)

                                pool += diff
                                self.properties[player].money -= diff
                                player_bets[player] = player_bets.get(player, 0) + diff
                    for player in folded_players:
                        remain_players.remove(player)
                    if not raised_player:
                        break
                remain_rounds -= 1


if __name__ == "__main__":
    HoldemGame().run()

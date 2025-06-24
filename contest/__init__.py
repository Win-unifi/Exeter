from otree.api import *

doc = """
 Tullock Lottery Contest - Prima esercitazione scuola estiva Exeter 2025
"""

class C(BaseConstants):
    NAME_IN_URL = 'contest'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 2
    ENDOWMENT = Currency(10)
    COST_PER_TICKET = Currency(0.50)
    PRIZE = Currency(8)

class Subsession(BaseSubsession):
    is_paid = models.BooleanField()

    def setup_round(self):
        self.is_paid = True
        for group in self.get_groups():
            group.setup_round()

    def compute_outcome(self):
        for group in self.get_groups():
            group.compute_outcome()

class Group(BaseGroup):
    prize = models.CurrencyField()

    def setup_round(self):
        self.prize = C.PRIZE
        for player in self.get_players():
            player.setup_round()

    def compute_outcome(self):
        total = sum(player.tickets_purchased for player in self.get_players())
        for player in self.get_players():
            try:
                player.prize_won = player.tickets_purchased / total
            except ZeroDivisionError:
                player.prize_won = 1 / len(self.get_players())
            player.earnings = (
                    player.endowment -
                    player.tickets_purchased * player.cost_per_ticket +
                    self.prize * player.prize_won
            )

class Player(BasePlayer):
    endowment = models.CurrencyField()
    cost_per_ticket = models.CurrencyField()
    tickets_purchased = models.IntegerField()
    prize_won = models.FloatField()
    earnings = models.CurrencyField()

    def setup_round(self):
        self.endowment = C.ENDOWMENT
        self.cost_per_ticket = C.COST_PER_TICKET

    @property
    def coplayer(self):
        return self.group.get_player_by_id(3 - self.id_in_group)

# Creates a global scope function alternative to having the SetupRound(WaitPage)
# def creating_session(subsession):
#    subsessionsetup_round().

# PAGES

class SetupRound(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        subsession.setup_round()

class Intro(Page):
    pass

class Decision(Page):
    form_model = "player"
    form_fields = ["tickets_purchased"]

class DecisionWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession):
        subsession.compute_outcome()

class Results(Page):
    pass
# Not good. Definition TOO LONG. Solution is easy: see Results.html
#    @staticmethod
#    def vars_for_template(player):
#        return {
#            "coplayer_purchase": player.group.get_player_by_id(3 - player.id_in_group).tickets_purchased
#       }

class EndBlock(Page):
    pass

page_sequence = [
    SetupRound,
    Intro,
    Decision,
    DecisionWaitPage,
    Results,
    EndBlock
]

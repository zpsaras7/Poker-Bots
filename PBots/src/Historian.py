class Historian:
    #Historian class that is only instantiated for every new game
    # not every new hand, keeps track of opponent's average statistics
    # in order to exploit their strategy
    
    #Total Game Stats
    num_hands_played = 0
    win_count = 0
    instant_fold = 0
    
    #Pre-Flop Stats
    pfr_count = 0
    vpip_count = 0
    init_fold_count = 0 #Related to vpip
    three_B_count = 0
    my_pfr_count = 0
    my_3_bet_count = 0
    pfr_fold_count = 0
    f_3_count = 0
    call_raise_count = 0
    check_raise_count = 0
    has_called_preflop = False
    has_checked_preflop = False
    poss_2_bet = 0
    poss_3_bet = 0
    
    #Post-Flop Stats
    agression_factor = 0.0 # (Raise% + Bet%) / Call%, only calculated post flop
    raise_count = 0
    bet_count = 0
    call_count = 0
    action_count = 0 #Post-Flop Rates
    wtsd_count = 0 #how often opponent goes to showdown after seeing flop (used w aggression)
    showdown_count = 0
    seen_flop_count = 0
    cb_count = 0
    two_B_count = 0
    my_C_bet = 0 #how many times we c-bet
    my_barrel = 0 #how many times we double barrel
    fb_count = 0 #fold to continuation bets
    f2_count = 0 #fold to second barrels
    sdw_count = 0
    fold_count = 0
    check_count = 0
    opp_check_this_street = False
    
    #Placeholders
    vpip = 0.8
    pfr = 0.5
    three_B = 0.45
    pfr_fold = 0.3
    three_B_fold = 0.4
    wtsd = 0.5
    cbet = 0.2
    db = 0.15
    cb_fold = 0.4
    b_fold = 0.4
    agression = 1.5
    sdw = 0.5
    aggrofreq = 0.5
    callraise = 0.0
    checkraise = 0.0
    two_B = 0.15
    
    def __init__(self, opponent_name, my_name, bb):
        self.my_name = my_name
        self.opponent_name = opponent_name
        self.bb = bb
        
    def update(self, action_params_list):
        self.last_actions = action_params_list
        postflop = True
        their_raise_count = 0
        my_raise_count = 0
        for params in action_params_list:
            if 'POST'.lower() == params['name'].lower():
                postflop = False
                self.has_called_preflop = False
                self.has_checked_preflop = False
            if not postflop:
                self.processPreflopAction(params, their_raise_count, my_raise_count)
            else:
                self.processPostflopAction(params, their_raise_count, my_raise_count)
            if 'WIN'.lower() == params['name'].lower():
                self.num_hands_played += 1
                if params['amount'] == (self.bb*3/2) and params['actor'].lower() == self.opponent_name.lower():
                    self.instant_fold += 1
                if params['actor'].lower() == self.my_name.lower():
                    self.win_count += 1
            elif 'TIE'.lower() == params['name'].lower():
                self.num_hands_played += 0.5
                    
    def processPreflopAction(self, action, their_raise_count, my_raise_count):
        try:
            if action['name'].lower() == 'RAISE'.lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    if their_raise_count == 0:
                        self.pfr_count += 1
                        if self.has_called_preflop:
                            self.call_raise_count += 1
                        if self.has_checked_preflop:
                            self.check_raise_count += 1
                    elif their_raise_count > 0 and my_raise_count > 0:
                        self.three_B_count += 1
                    elif their_raise_count == 0 and my_raise_count == 1:
                        self.two_B_count += 1
                    their_raise_count += 1
                    self.pfr_count += 1
                else:
                    if my_raise_count == 0:
                        self.poss_2_bet += 1
                    elif my_raise_count > 0 and their_raise_count > 0:
                        self.poss_3_bet += 1
                        self.my_3_bet_count += 1
                    my_raise_count += 1
                    self.my_pfr_count += 1
                    
            elif action['name'].lower() == "FOLD".lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    if their_raise_count == 0 and my_raise_count == 1:
                        self.pfr_fold_count += 1
                    elif their_raise_count == 1 and my_raise_count == 1:
                        self.f_3_count += 1
            
            elif action['name'].lower() == "CALL".lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    self.has_called_preflop = True
                    self.call_count += 1
                    
            elif action['name'].lower() == "CHECK".lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    self.has_checked_preflop = True
                    self.check_count += 1
        except:
            return
                
    def processPostflopAction(self, action, their_raise_count, my_raise_count):
        try:
            if action['name'].lower() == 'DEAL'.lower():
                if action['street'].lower() == 'FLOP'.lower():
                    self.seen_flop_count += 1
                self.opp_check_this_street = False
            
            if action['name'].lower() == 'SHOW'.lower():
                self.showdown_count += (1./2) #2 shows per showdown
            
            elif action['name'].lower() == 'BET'.lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    self.cb_count += 1
                    self.bet_count += 1
                    self.action_count += 1
                elif action['actor'].lower() == self.my_name.lower():
                    self.my_C_bet += 1
            
            elif action['name'].lower() == 'RAISE'.lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    if their_raise_count == 0:
                        if self.has_called_preflop:
                            self.call_raise_count += 1
                        if self.has_checked_preflop:
                            self.check_raise_count += 1
                        self.raise_count += 1
                    elif their_raise_count > 0 and my_raise_count > 0:
                        self.three_B_count += 1
                    elif their_raise_count == 0 and my_raise_count == 1:
                        self.two_B_count += 1
                    their_raise_count += 1
                    self.action_count += 1
                else:
                    if my_raise_count == 0:
                        self.poss_2_bet += 1
                    elif my_raise_count > 0 and their_raise_count > 0:
                        self.poss_3_bet += 1
                        self.my_3_bet_count += 1
                    my_raise_count += 1
                    self.my_pfr_count += 1
                    
            elif action['name'].lower() == "FOLD".lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    if their_raise_count == 0 and my_raise_count == 0:
                        self.fb_count += 1
                    elif their_raise_count == 0 and my_raise_count == 1:
                        self.f2_count += 1
                    self.action_count += 1
            
            elif action['name'].lower() == "CALL".lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    self.call_count += 1
                    self.action_count += 1
     
            elif action['name'].lower() == "CHECK".lower():
                if action['actor'].lower() == self.opponent_name.lower():
                    self.opp_check_this_street = True
                    self.check_count += 1
                    self.action_count += 1
        except:
            return
                
    def getPFR(self):
        pfr_rate = self.pfr_count / max(1, (self.num_hands_played - self.instant_fold))
        return (25.0*self.pfr + pfr_rate*(self.num_hands_played - self.instant_fold))/ ((self.num_hands_played-self.instant_fold) + 25.0)
     
    def getCallRaise(self):
        call_raise_rate = self.call_raise_count / max(1, (self.num_hands_played - self.instant_fold))
        return (50*self.callraise + call_raise_rate*(self.num_hands_played - self.instant_fold))/((self.num_hands_played - self.instant_fold) + 50)
     
    def getCheckRaise(self):
        check_raise_rate = self.check_raise_count / max(1, self.seen_flop_count)
        return (50*self.callraise + check_raise_rate*self.seen_flop_count) / (self.seen_flop_count +50)
     
    def get3BetRate(self):
        threeBRate = float(self.three_B_count)/(max(1, self.poss_3_bet))
        return (50*self.three_B + threeBRate*self.poss_3_bet)/(self.poss_3_bet + 50)
    
    def get2BetRate(self):
        twoBRate = float(self.two_B_count)/max(1, self.poss_2_bet)
        return (50*self.two_B + twoBRate*self.poss_2_bet)/(self.poss_2_bet + 50)
    
    def getAgression(self):
        rate = float(self.raise_count+self.bet_count) / max(1, self.call_count)
        return (200*self.agression + rate*self.action_count)/ (200 + self.action_count)
    
    def getAggroFreq(self):
        actions  = self.raise_count + self.bet_count + self.call_count + self.fold_count + self.check_count
        rate = float(self.raise_count+self.bet_count) / max(1, actions)
        return (100*self.aggrofreq + rate*actions) / (100+actions)
        
    
# ADD PRINTING TO FILE FOR ALL OF THE VARIABLES
    
                    
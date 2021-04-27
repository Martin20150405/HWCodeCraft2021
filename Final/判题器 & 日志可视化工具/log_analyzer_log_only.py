#!/usr/bin/python3

# 由于正式赛会换数据并且不公开，只开放log下载
# in case we have log but not dataset
# usage: python log_parser.py -f a.zip -w 1
# (if you win and are analyzing a.zip)

import zipfile
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm

def unzip(file_name):
    if file_name.endswith(".zip"):
        zip_file = zipfile.ZipFile(file_name)
        for names in zip_file.namelist():
            zip_file.extract(names,'.')
        zip_file.close()

class PlayerState:
    def __init__(self,postfix):
        self.postfix = postfix
        self.give_up_rate = []

        self.total_profits = []
        self.daily_profits = []
        self.total_incomes = []
        self.daily_incomes = []
        self.total_costs = []
        self.daily_costs = []

        self.daily_mean_income_list = []
        self.daily_bid_list = []
        self.daily_total_bid_list = []
        self.success_rate = []

        self.success_num = 0
        self.give_up_num = 0
        self.daily_income = 0
        self.daily_bid = 0
        self.bid_cnt = 0

    def bid(self,px,py):
        self.give_up_num += 1 if px == -1 else 0
        # px = -INF py = -INF
        # px normal py -INF
        # py -INF py normal
        lpx, lpy = len(px), len(py)
        px,py = px[0],py[0]
        if lpx==1 and lpy == 1:
            pass
        elif lpx==1 and lpy==2:
            if px != -1:
                px = py+1
        elif lpx==2 and lpy==1:
            if py != -1:
                py = px+1
        else:
            pass

        if px != -1:
            self.bid_cnt += 1
            self.daily_bid += px
        if px != -1 and (px <= py or py == -1):
            self.success_num += 1
            self.daily_income += px

    def update(self,add_cnt,profit):
        self.daily_profits.append(profit if len(self.total_profits)==0 else profit - self.total_profits[-1])
        self.total_profits.append(profit)
        self.daily_incomes.append(self.daily_income)
        self.total_incomes.append(self.total_incomes[-1]+self.daily_incomes[-1] if len(self.total_incomes)>0 else self.daily_incomes[-1])
        self.daily_costs.append(self.daily_incomes[-1] - self.daily_profits[-1])
        self.total_costs.append(self.total_costs[-1]+self.daily_costs[-1] if len(self.total_costs)>0 else self.daily_costs[-1])

        self.daily_total_bid_list.append(self.daily_bid)

        if self.success_num != 0:
            self.daily_mean_income_list.append(self.daily_income / self.success_num)
        else:
            self.daily_mean_income_list.append(0)

        if self.bid_cnt != 0:
            self.daily_bid_list.append(self.daily_bid / self.bid_cnt)
        else:
            self.daily_bid_list.append(0)

        self.give_up_rate.append(self.give_up_num / add_cnt)
        self.success_rate.append(self.success_num / add_cnt)

        # clear state
        self.success_num = 0
        self.daily_income = 0
        self.daily_bid = 0
        self.bid_cnt = 0
        self.give_up_num = 0

    def replace_content(self,content,key,data):
        return content.replace(key+self.postfix,str(data))

def parse_log(file_name,won_combat):
    log_file = open(file_name,'r')
    log_time = log_file.readline().strip().split('e:')[-1]
    test_file_name = log_file.readline().strip().split('\'')[1]

    input_lines = log_file.readlines()
    RUNNING_LOG = input_lines[-2].strip()
    input_lines.pop(-1)
    input_lines.pop(-1)

    num_days = -1
    for x in input_lines:
        if 'Day' in x:
            num_days = max(num_days,int(x.split()[-1]))

    description = 'Time: %s Dataset:[%s] Day:[%d]'%(log_time,test_file_name,num_days)
    print(description)

    '''
    Part 1
    A.Profit.双方每日收益、总收益变化（收益=进账-成本）
    B.Income.双方每日进账、总进账
    C.Cost.双方每日成本、总成本
    
    2.每日增加请求数
    3.每日竞价成功率
    4.双方每日放弃请求率
    5.双方每日开价均值、获取到的利润均值
    6.双方每日开价总和、获取到的利润总和（和每日进账重复了）
    '''

    add_count_list = []
    line_idx = 0

    player_0, player_1 = PlayerState('_0'),PlayerState('_1')

    for r in tqdm(range(num_days)):
        add_cnt = 0
        line_idx+=2
        while True:
            ri = input_lines[line_idx].strip()
            if 'Profit' in ri:
                break
            line_idx+=1

            p0, p1 = ri.split()
            add_cnt += 1
            if p0[-1] == '#':
                p0 = int(p0.split(',')[0])
                p0 = [p0,'#']
            else:
                p0 = int(p0)
                p0 = [p0]
            if p1[-1] == '#':
                p1 = int(p1.split(',')[0])
                p1 = [p1,'#']
            else:
                p1 = int(p1)
                p1 = [p1]
            player_0.bid(p0, p1)
            player_1.bid(p1, p0)
        profits = list(map(int,input_lines[line_idx].strip().split(':')[-1].split()))
        line_idx+=1
        player_0.update(add_cnt, profits[0])
        player_1.update(add_cnt, profits[1])
        add_count_list.append(add_cnt)

    contents = Path('template.htm').read_text()
    contents = contents.replace('PLACEHOLDER_DESCRIPTION',description)
    contents = contents.replace('PLACEHOLDER_RUNNING_LOG',RUNNING_LOG)
    contents = contents.replace('PLACEHOLDER_ADD_REQUEST_NUM',str(add_count_list))

    contents = player_0.replace_content(contents, 'PLACEHOLDER_TOTAL_PROFIT', player_0.total_profits)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_TOTAL_PROFIT', player_1.total_profits)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_DAILY_PROFIT', player_0.daily_profits)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_DAILY_PROFIT', player_1.daily_profits)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_TOTAL_INCOME', player_0.total_incomes)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_TOTAL_INCOME', player_1.total_incomes)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_DAILY_INCOME', player_0.daily_incomes)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_DAILY_INCOME', player_1.daily_incomes)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_TOTAL_COST', player_0.total_costs)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_TOTAL_COST', player_1.total_costs)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_DAILY_COST', player_0.daily_costs)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_DAILY_COST', player_1.daily_costs)

    contents = player_0.replace_content(contents, 'PLACEHOLDER_DAILY_BID', player_0.daily_bid_list)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_DAILY_BID', player_1.daily_bid_list)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_TOTAL_DAILY_BID', player_0.daily_total_bid_list)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_TOTAL_DAILY_BID', player_1.daily_total_bid_list)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_MEAN_DAILY_INCOME', player_0.daily_mean_income_list)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_MEAN_DAILY_INCOME', player_1.daily_mean_income_list)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_BID_SUCCESS_RATE', player_0.success_rate)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_BID_SUCCESS_RATE', player_1.success_rate)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_GIVE_UP_RATE', player_0.give_up_rate)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_GIVE_UP_RATE', player_1.give_up_rate)

    winner = 0 if player_0.total_profits[-1] > player_1.total_profits[-1] else 1
    our_id = winner if won_combat else 1-winner
    rival_id = 1-our_id
    contents = contents.replace('Player %d'%our_id, 'P%d-us'%our_id)
    contents = contents.replace('Player %d'%rival_id, 'P%d-rival'%rival_id)

    with open(file_name.replace('.log','.html'),'w') as f:
        f.write(contents)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="log file of *.zip or *.txt", required=True, type=str)
    parser.add_argument("-w", "--win", help="1 if you win else 0", required=True, type=int)
    args = parser.parse_args()

    file_name = args.file
    won_combat = args.win

    unzip(file_name)
    parse_log(file_name.replace('.zip','.log'),won_combat)
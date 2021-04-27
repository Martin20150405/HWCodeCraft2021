#!/usr/bin/python3

# usage: python log_parser.py -f a.zip -w 1
# (if you win and are analyzing a.zip)

import zipfile
import sys
import argparse
import numpy as np
from pathlib import Path
from tqdm import tqdm
from reader import parse_host_vm_info,get_requests_data

def unzip(file_name):
    if file_name.endswith(".zip"):
        zip_file = zipfile.ZipFile(file_name)
        for names in zip_file.namelist():
            zip_file.extract(names,'.')
        zip_file.close()

class PlayerState:
    def __init__(self,postfix):
        self.postfix = postfix
        self.mean_discounts = []
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
        self.vm_num_list = []
        self.success_rate = []
        self.discounts = []
        self.vms = set()

        self.success_num = 0
        self.give_up_num = 0
        self.daily_income = 0
        self.daily_bid = 0
        self.bid_cnt = 0

    def bid(self,px,py,vm_id,offered_price):
        self.give_up_num += 1 if px == -1 else 0
        if px != -1:
            self.bid_cnt += 1
            self.daily_bid += px
            discount = px / offered_price
            self.discounts.append(discount)
        if px != -1 and (px <= py or py == -1):
            self.success_num += 1
            self.vms.add(vm_id)
            self.daily_income += px

    def delete(self,vm_id):
        self.vms.discard(vm_id)

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

        self.mean_discounts.append(np.mean(np.array(self.discounts)))
        self.give_up_rate.append(self.give_up_num / add_cnt)
        self.success_rate.append(self.success_num / add_cnt)
        self.vm_num_list.append(len(self.vms))

        # clear state
        self.success_num = 0
        self.daily_income = 0
        self.daily_bid = 0
        self.bid_cnt = 0
        self.give_up_num = 0
        self.discounts = []

    def replace_content(self,content,key,data):
        return content.replace(key+self.postfix,str(data))

def parse_log(file_name,won_combat):
    log_file = open(file_name,'r')
    log_time = log_file.readline().strip().split('e:')[-1]
    test_file_name = log_file.readline().strip().split('\'')[1]
    with open(test_file_name, 'r') as f:
        input_lines = f.readlines()
    num_hosts,host_infos,num_vms,vm_infos = parse_host_vm_info(input_lines)
    input_lines = input_lines[num_hosts + num_vms + 2:]
    num_days, num_knows = map(int, input_lines[0].strip().split())
    description = 'Time: %s Dataset:[%s] Server:[%d] VM:[%d] Day:[%d] K:[%d]'%(log_time,test_file_name,num_hosts,num_vms,num_days,num_knows)
    print(description)
    requests = get_requests_data(input_lines)

    '''
    Part 1
    A.Profit.双方每日收益、总收益变化（收益=进账-成本）
    B.Income.双方每日进账、总进账
    C.Cost.双方每日成本、总成本
    
    2.每日请求数，虚拟机数量变化
    3.双方每日/每请求折扣变化
    4.每日竞价/加权竞价成功率
    5.双方每日放弃请求率/加权放弃请求率
    6.双方每日开价均值、获取到的利润均值
    7.每日用户报价均值（报价除以生存时间除以资源总量）
    8.双方每日开价总和、获取到的进账总和（和每日进账重复了）
    =_= 加权偷懒没有做
    '''

    daily_price_factor_list = []
    add_count_list = []
    del_count_list = []

    player_0, player_1 = PlayerState('_0'),PlayerState('_1')

    for r in tqdm(requests):
        log_file.readline()
        log_file.readline()
        # in range of add

        add_cnt = 0
        del_cnt = 0
        price_factors = []
        for ri in r:
            if 'add' in ri:
                offered_price = int(ri.split(',')[-1][:-2])
                life_time = int(ri.split(',')[-2])
                vm_id = int(ri.split(',')[-3])
                vm_name = ri.split(',')[-4].replace(' ', '')
                vm_info = vm_infos[vm_name]
                price_factor = offered_price/life_time/(vm_info.cpu*2.3 + vm_info.mem)
                price_factors.append(price_factor)
                p0,p1 = map(int,log_file.readline().split())
                add_cnt += 1

                player_0.bid(p0,p1,vm_id,offered_price)
                player_1.bid(p1,p0,vm_id,offered_price)
            else:
                vm_id = int(ri.split(',')[-1][:-2])
                player_0.delete(vm_id)
                player_1.delete(vm_id)
                del_cnt += 1
        profits = list(map(int,log_file.readline().split(':')[-1].split()))
        player_0.update(add_cnt,profits[0])
        player_1.update(add_cnt,profits[1])

        add_count_list.append(add_cnt)
        del_count_list.append(del_cnt)
        daily_price_factor_list.append(np.mean(np.array(price_factors)))

    contents = Path('template.htm').read_text()
    contents = contents.replace('PLACEHOLDER_DESCRIPTION',description)
    contents = contents.replace('PLACEHOLDER_RUNNING_LOG',log_file.readline().strip())
    contents = contents.replace('PLACEHOLDER_ADD_REQUEST_NUM',str(add_count_list))
    contents = contents.replace('PLACEHOLDER_DEL_REQUEST_NUM',str(del_count_list))
    contents = contents.replace('PLACEHOLDER_PRICE_FACTOR',str(daily_price_factor_list))

    contents = player_0.replace_content(contents,'PLACEHOLDER_VM_NUM',player_0.vm_num_list)
    contents = player_1.replace_content(contents,'PLACEHOLDER_VM_NUM',player_1.vm_num_list)

    contents = player_0.replace_content(contents,'PLACEHOLDER_TOTAL_PROFIT',player_0.total_profits)
    contents = player_1.replace_content(contents,'PLACEHOLDER_TOTAL_PROFIT',player_1.total_profits)
    contents = player_0.replace_content(contents,'PLACEHOLDER_DAILY_PROFIT',player_0.daily_profits)
    contents = player_1.replace_content(contents,'PLACEHOLDER_DAILY_PROFIT',player_1.daily_profits)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_TOTAL_INCOME', player_0.total_incomes)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_TOTAL_INCOME', player_1.total_incomes)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_DAILY_INCOME', player_0.daily_incomes)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_DAILY_INCOME', player_1.daily_incomes)
    contents = player_0.replace_content(contents,'PLACEHOLDER_TOTAL_COST',player_0.total_costs)
    contents = player_1.replace_content(contents,'PLACEHOLDER_TOTAL_COST',player_1.total_costs)
    contents = player_0.replace_content(contents,'PLACEHOLDER_DAILY_COST',player_0.daily_costs)
    contents = player_1.replace_content(contents,'PLACEHOLDER_DAILY_COST',player_1.daily_costs)

    contents = player_0.replace_content(contents, 'PLACEHOLDER_DAILY_BID', player_0.daily_bid_list)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_DAILY_BID', player_1.daily_bid_list)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_TOTAL_DAILY_BID', player_0.daily_total_bid_list)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_TOTAL_DAILY_BID', player_1.daily_total_bid_list)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_MEAN_DAILY_INCOME', player_0.daily_mean_income_list)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_MEAN_DAILY_INCOME', player_1.daily_mean_income_list)
    contents = player_0.replace_content(contents, 'PLACEHOLDER_MEAN_DISCOUNT_RATE', player_0.mean_discounts)
    contents = player_1.replace_content(contents, 'PLACEHOLDER_MEAN_DISCOUNT_RATE', player_1.mean_discounts)
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
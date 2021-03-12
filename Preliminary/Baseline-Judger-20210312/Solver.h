//
// Created by QAQ on 2021/3/11.
//

#ifndef HWCODECRAFT2021_SOLVER_H
#define HWCODECRAFT2021_SOLVER_H

#include "IOUtil.h"

class Solver {

public:
    Solver(IOUtil *ioUtil, int totalDays);

    void dailyRoutine(int day);

    void displayCost();

    double getServerWeight(ServerType &serverType);

private:
    IOUtil *ioUtil;


    // current bought servers
    std::vector<Server> currentServers;

    // map request ID to Server instance and insert type
    // to resolve corresponding VM, use virtualHosts[requestIDMap[requestID]] or virtualHosts[request.virtualHostName]
    std::unordered_map<int,std::pair<int,int>> requestMap;

    int currentDay,totalDays;
    std::unordered_map<std::string,int> serversToBuy;
    ull serverCost,powerCost;

    void purchase();

    void distribute();

    void migrate();

    int fitServer(Server &server, Request &request);

};


#endif //HWCODECRAFT2021_SOLVER_H

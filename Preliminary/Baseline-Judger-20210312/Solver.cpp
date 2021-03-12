//
// Created by QAQ on 2021/3/11.
//

#include "Solver.h"

double Solver::getServerWeight(ServerType &serverType){
    return serverType.coreNum*0.75 + serverType.memorySize*0.22 + serverType.hardwareCost*0.01 + serverType.dailyCost*0.02*(totalDays-currentDay);
}

void Solver::purchase(){
    // TODO:select proper server to purchase
    // magic，赐我力量

    //买！买最贵的！！
    ServerType &serverType = ioUtil->serverTypes[13];
    serversToBuy[serverType.name]++;

    currentServers.emplace_back(serverType,currentServers.size());
}

int Solver::fitServer(Server &server, Request &request){
    VirtualHost& virtualHost = ioUtil->virtualHosts[request.virtualHostName];
    bool fit = false;
    int coreCost = virtualHost.coreNum, memoryCost = virtualHost.memorySize;
    if(virtualHost.crossNUMA){
        coreCost/=2; memoryCost/=2;
        fit = server.fit(server.A,coreCost, memoryCost)
                && server.fit(server.B,coreCost, memoryCost);
        if(fit){
            server.A.first -= coreCost;
            server.B.first -= coreCost;
            server.A.second -= memoryCost;
            server.B.second -= memoryCost;
            return DEPLOY_AB;
        }
    }else{
        fit |= server.fit(server.A, coreCost, memoryCost);
        if(fit){
            server.A.first -= coreCost;
            server.A.second -= memoryCost;
            return DEPLOY_A;
        }else{
            fit |= server.fit(server.B, coreCost, memoryCost);
            if(fit){
                server.B.first -= coreCost;
                server.B.second -= memoryCost;
                return DEPLOY_B;
            }
        }
    }
    return UNFIT;
}

void Solver::distribute() {
    std::vector<Request> &requests = ioUtil->allRequests[currentDay];
    int previousServerNum = currentServers.size();

    // 生成要购买的服务器序列
    for(Request& request:requests){
        if(request.operation == ADD){
            bool flag = false;
            while(true){
                for(Server &server:currentServers){
                    int ret;
                    if((ret = fitServer(server,request))!=UNFIT){
                        server.requestIDs.insert(request.requestID);
                        requestMap[request.requestID] = {server.id,ret};
                        flag = true;
                        break;
                    }
                }
                if(flag) break;
                purchase();
            }
        }else{
            // delete
            auto &ret = requestMap[request.requestID];
            Server &server = currentServers[ret.first];
            VirtualHost &virtualHost = ioUtil->virtualHosts[request.virtualHostName];
            server.requestIDs.erase(request.requestID);
            if(ret.second == DEPLOY_AB){
                server.A.first+=virtualHost.coreNum/2;
                server.B.first+=virtualHost.coreNum/2;
                server.A.second+=virtualHost.memorySize/2;
                server.B.second+=virtualHost.memorySize/2;
            }else{
                if(ret.second == DEPLOY_A){
                    server.A.first+=virtualHost.coreNum;
                    server.A.second+=virtualHost.memorySize;
                }else{
                    server.B.first+=virtualHost.coreNum;
                    server.B.second+=virtualHost.memorySize;
                }
            }
        }
    }

    // 重映射id 以保证服务器是批量购买
    ioUtil->addOutput("(purchase, "+std::to_string(serversToBuy.size())+")");

    int currentServerNum = currentServers.size();
    int currentID = previousServerNum;
    for(int i=previousServerNum;i<currentServerNum;i++){
        Server &server = currentServers[i];
        if(server.remappedID == -1){
            int num = serversToBuy[server.serverType.name];
            serverCost+=server.serverType.hardwareCost*(ull)num;
            ioUtil->addOutput("("+server.serverType.name+", "+std::to_string(num)+")");
            for(int j=i;j<currentServerNum;j++){
                if(server.serverType.name == currentServers[j].serverType.name){
                    currentServers[j].remappedID = currentID++;
                }
            }
        }
    }
    serversToBuy.clear();

    migrate();

    // 输出add操作对应的分配序列
    for(Request& request:requests){
        if(request.operation == ADD){
            auto &ret = requestMap[request.requestID];
            Server &server = currentServers[ret.first];
            std::string tmpStr = "("+std::to_string(server.remappedID);
            if(ret.second == DEPLOY_AB){
                ioUtil->addOutput(tmpStr+")");
            }else if(ret.second == DEPLOY_A){
                ioUtil->addOutput(tmpStr+", A)");
            }else ioUtil->addOutput(tmpStr+", B)");
        }
    }

    // compute daily cost
    for(Server &server:currentServers){
        if(!server.requestIDs.empty()) powerCost+=server.serverType.dailyCost;
    }
}

void Solver::migrate() {
    ioUtil->addOutput("(migration, 0)");
}

void Solver::dailyRoutine(int day) {
    currentDay = day;

    distribute();
}

Solver::Solver(IOUtil *ioUtil, int totalDays) : ioUtil(ioUtil), totalDays(totalDays) {
    serverCost = powerCost = 0;
}

void Solver::displayCost() {
    std::cout<<"ServerCost: "<<serverCost<<"\nPowerCost: "<<powerCost<<"\nTotal: "<<serverCost+powerCost<<std::endl;
}

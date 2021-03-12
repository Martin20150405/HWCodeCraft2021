//
// Created by QAQ on 2021/3/11.
//

#ifndef HWCODECRAFT2021_GLOBALDEFINITION_H
#define HWCODECRAFT2021_GLOBALDEFINITION_H

#include <bits/stdc++.h>

//#define TEST
//#define VERBOSE

#ifdef TEST
const std::string testFilePath = "training-2.txt";
#endif

typedef uint64_t ull;
typedef int64_t ll;
typedef uint32_t ui;

enum Operation{
    ADD,DEL,
    PURCHASE,MIGRATE,
    DEPLOY_A,DEPLOY_B,DEPLOY_AB,UNFIT
};

struct ServerType{
    std::string name;
    int coreNum, memorySize, hardwareCost, dailyCost;

    std::string toString(){
        char buf[1024]={0};
        sprintf(buf,"Name:[%s] coreNum:[%d] memorySize:[%d] hardwareCost:[%d] dailyCost:[%d]",name.c_str(),coreNum,memorySize,hardwareCost,dailyCost);
        return buf;
    }
};

struct VirtualHost{
    std::string name;
    int coreNum, memorySize, crossNUMA;

    std::string toString(){
        char buf[1024]={0};
        sprintf(buf,"Name:[%s] coreNum:[%d] memorySize:[%d] crossNUMA:[%d]",name.c_str(),coreNum,memorySize,crossNUMA);
        return buf;
    }
};

struct Request{
    int operation;
    std::string virtualHostName;
    int requestID; // 创建请求的虚拟机ID唯一

    std::string toString(){
        char buf[1024]={0};
        sprintf(buf,"Operation:[%s] virtualHostName:[%s] requestID:[%d]",operation==ADD? "add":"del",virtualHostName.c_str(),requestID);
        return buf;
    }
};

// 具体的服务器实例
struct Server{
    int id; //在服务器集合中的下标
    int remappedID; //实际购买序列中的id

    ServerType serverType;

    //current resource
    std::pair<int, int> A, B;

    //map server to request ID
    std::unordered_set<int> requestIDs;

    Server() = default;
    Server(const ServerType & _s,int _id) {
        id = _id;
        remappedID = -1;
        serverType = _s;
        A = {_s.coreNum / 2, _s.memorySize / 2};
        B = {_s.coreNum / 2, _s.memorySize / 2};
    }

    bool fit(std::pair<int, int>& C,int coreNum,int memorySize){
        return C.first>=coreNum && C.second>=memorySize;
    }
};
#endif //HWCODECRAFT2021_GLOBALDEFINITION_H

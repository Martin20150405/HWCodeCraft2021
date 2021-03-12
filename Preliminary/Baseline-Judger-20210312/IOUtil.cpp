//
// Created by QAQ on 2021/3/11.
//

#include "IOUtil.h"

IOUtil::IOUtil() {
#ifdef TEST
    std::freopen(testFilePath.c_str(),"r",stdin);
#endif
}

int IOUtil::readServerTypes() {
    int serverTypeNum;
    std::cin>>serverTypeNum;
    std::cin.ignore(1024, '\n');
    //read server types
    for (int i = 0; i < serverTypeNum; ++i) {
        std::cin.ignore();
        std::string tempStr;
        getline(std::cin, tempStr);
        tempStr.pop_back();

        auto fields = split(tempStr,',');

        std::string name = fields[0];
        int coreNum = std::stoi(fields[1]);
        int memorySize = std::stoi(fields[2]);
        int hardwareCost = std::stoi(fields[3]);
        int dailyCost = std::stoi(fields[4]);
        serverTypes.push_back({name, coreNum, memorySize, hardwareCost, dailyCost});
        serverTypeMap[name] = serverTypes.back();

#ifdef VERBOSE
        std::cout<<"Server-" <<i+1<<" "<<serverTypeMap[name].toString()<<std::endl;
#endif
    }
    return serverTypeNum;
}

int IOUtil::readVirtualHosts() {
    int virtualHostNum;
    std::cin>>virtualHostNum;
    std::cin.ignore(1024, '\n');
    //read virtual hosts types
    for (int i = 0; i < virtualHostNum; ++i) {
        std::cin.ignore();
        std::string tempStr;
        getline(std::cin, tempStr);
        tempStr.pop_back();

        auto fields = split(tempStr,',');

        std::string name = fields[0];
        int coreNum = std::stoi(fields[1]);
        int memorySize = std::stoi(fields[2]);
        int crossNUMA = std::stoi(fields[3]);
        virtualHosts[name] = {name, coreNum, memorySize, crossNUMA};

#ifdef VERBOSE
        std::cout<<"VirtualHost-"<<i+1<<" "<<virtualHosts[name].toString()<<std::endl;
#endif
    }
    return virtualHostNum;
}

int IOUtil::readInt() {
    int ret;
    std::cin>>ret;
    return ret;
}

int IOUtil::readRequests() {
    std::vector<Request> requests;
    int requestNum;
    std::cin>>requestNum;
    std::cin.ignore(1024, '\n');
    for (int i = 0; i < requestNum; ++i) {
        std::cin.ignore();
        std::string tempStr;
        getline(std::cin, tempStr);
        tempStr.pop_back();

        auto fields = split(tempStr,',');

        //对于删除操作，保证ID对应的虚拟机一定存在
        int operation = (fields[0]=="add")? ADD:DEL;
        std::string virtualHostName;
        int requestID;
        if(operation == ADD){
            virtualHostName = fields[1].substr(1);
            requestID = std::stoi(fields[2]);
            requestIDMap[requestID] = virtualHostName;
        }else{
            //delete
            requestID = std::stoi(fields[1]);
            virtualHostName = requestIDMap[requestID];
        }
        requests.push_back({operation,virtualHostName,requestID});
#ifdef VERBOSE
        //std::cout<<"Request-"<<i+1<<" "<<requests.back().toString()<<std::endl;
#endif
    }
    allRequests.emplace_back(requests);
    return requestNum;
}

std::vector<std::string> IOUtil::split(std::string tempStr, char c) {
    auto ret = std::vector<std::string>();
    size_t pos;
    while((pos = tempStr.find(c))!=std::string::npos){
        ret.emplace_back(tempStr.substr(0, pos));
        tempStr = tempStr.substr(pos + 1);
    }
    ret.emplace_back(tempStr);
    return ret;
}

void IOUtil::addOutput(std::string s) {
#ifdef VERBOSE
//    std::cout<<s<<std::endl;
#endif
    outputs.emplace_back(s);
}



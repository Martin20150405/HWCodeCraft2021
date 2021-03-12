//
// Created by QAQ on 2021/3/11.
//

#ifndef HWCODECRAFT2021_IOUTIL_H
#define HWCODECRAFT2021_IOUTIL_H

#include "GlobalDefinition.h"

struct IOUtil {
public:
    IOUtil();
    int readServerTypes();
    int readVirtualHosts();
    int readInt();
    int readRequests();
    std::vector<std::string> split(std::string tempStr, char c);
    void addOutput(std::string s);

    std::vector<ServerType> serverTypes;
    std::unordered_map<std::string,ServerType> serverTypeMap;
    std::unordered_map<std::string,VirtualHost> virtualHosts;
    // map requestID to VM name
    std::unordered_map<int,std::string> requestIDMap;

    std::vector<std::vector<Request>> allRequests;

    std::vector<std::string> outputs;

};


#endif //HWCODECRAFT2021_IOUTIL_H

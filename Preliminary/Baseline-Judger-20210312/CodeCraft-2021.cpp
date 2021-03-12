#include "IOUtil.h"
#include "Solver.h"
#include "OfflineJudger.h"

int main(){

	// [1] read standard input
    IOUtil ioUtil;
    // N: 服务器数量 [1,100]
    int N = ioUtil.readServerTypes();
    // M: 虚拟机数量 [1,1000]
    int M = ioUtil.readVirtualHosts();
    // T: 天数 [1,1000]
    int T = ioUtil.readInt();

    Solver solver(&ioUtil,T);
    // R: 每天的请求数 sum<=1e5
    for(int ti = 0; ti < T; ti++){
#ifdef VERBOSE
        if(ti % 100 == 0)
            printf("process day %d\n",ti);
#endif
        int R = ioUtil.readRequests();
        // [2] process
        solver.dailyRoutine(ti);
    }
#ifdef TEST
    solver.displayCost();
    std::freopen("output.txt","w",stdout);
#endif

    // [3] write standard output
    for(auto &s:ioUtil.outputs){
        std::cout<<s<<"\n";
    }

    // [4] flush stdout
	fflush(stdout);

#ifdef TEST
    freopen("CON", "w", stdout);
    std::cout<<"========= Here begins Judger's output =========\n";
    runJudger(testFilePath,"output.txt");
#endif
	return 0;
}

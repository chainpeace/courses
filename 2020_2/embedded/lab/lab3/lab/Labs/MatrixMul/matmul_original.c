#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>		//close()
#include <malloc.h>
#include <fcntl.h>
#include "../Profiler/profiler.h"
#include "/home/dusol/intel/advisor_2020.2.0.606470/include/advisor-annotate.h"

#define min(a, b) ((a) < (b) ? (a) : (b))

int check_result(int *x_origin, int *x_blocking, int N) {
	int i, j, diff_count = 0;

	for(i=0;i<N;i++) {
		for(j=0;j<N;j++) {
			if(x_origin[i*N+j] != x_blocking[i*N+j]) diff_count++;
		}
	}

	if(diff_count) 
		return 0;
	else 
		return 1;
}


int main(int argc, char **argv) {
	int *x_origin, *x_blocking, *y, *z;
	int i, j, k, r;
	int jj, kk;
	int N, B;
	
	if(argc == 1) {
		printf("[ERROR] Please Input the Matrix Size(N) and Blocking Size(B)\n");
		return 0;
	}

	N = atoi(argv[1]);
    B = atoi(argv[2]);

	/***** The result for original code *****/
	x_origin = (int *)malloc(N*N*sizeof(int));
	/****************************************/

	/***** The result for blocking code *****/
	x_blocking = (int *)malloc(N*N*sizeof(int));
	/****************************************/
	
	y = (int *)malloc(N*N*sizeof(int));
	z = (int *)malloc(N*N*sizeof(int));

	
    
    //-------------------------------
	// Original code
	//-------------------------------
	// Initialization
	for(i=0;i<N;i++) {
		for(j=0;j<N;j++) {
			x_origin[i*N+j] = 0;
			y[i*N+j] = 2;
			z[i*N+j] = 3;
		}
	}

    printf ("Matrix multiplication: original code\n");

    for(i=0;i<N;i++){
        for(j=0;j<N;j++){
            r=0;
            for(k=0;k<N;k++){
                r+=y[i*N+k]*z[k*N+j];
            }
            x_origin[i*N+j]=r;
        }
    }

	// You can Verify the result using check_result()
		/*
	if(check_result(x_origin, x_blocking, N)) 
		printf("Your answer is OK.\n");
	else
		printf("Your answer is Wrong.\n");
		*/

	free(x_origin);
	free(x_blocking);
	free(y);
	free(z);
	
	return 0;
}

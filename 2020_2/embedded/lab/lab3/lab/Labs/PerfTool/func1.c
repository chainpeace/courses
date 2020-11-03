#include <stdlib.h>

#define N 10000000
int sum(int n, int *arr);

int main() {
	int i, r;
	int* arr;

	arr = (int *) malloc (sizeof(int) * N);
	for (i = 0; i < N; i++) {
		arr[i] = i/10000;
	}

	r = sum(N, arr);
	return r;
}

int sum(int n, int *arr)
{
	int i;
	int r = 0;
	for (i =0; i < n; i++) {
		r += arr[i];
	}
	return r;
}

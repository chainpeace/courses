#include <stdio.h>
int fibonacci(n) {
	if (n == 0 || n == 1) return 1;
	else return fibonacci(n - 1) + fibonacci(n - 2);
}
int main()
{
	fibonacci(38);
	return 0;
}

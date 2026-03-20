#include<stdio.h>
#include<stdlib.h>
#define MAX_SIZE 100

typedef struct {
    int data[MAX_SIZE];
    int top;
} Stack;

void initialize(Stack *s) {
    s -> top = -1;
}

int isEmpty(Stack *s) {
    return s -> top == -1;
}

int isFull(Stack *s) {
    return s -> top == MAX_SIZE - 1;
}

void push(Stack *s, int value) {
    if (isFull(s)) {
        printf("Stack Overflow\n");
        return;
    }
    s -> data[++(s -> top)] = value;
}

int pop(Stack *s) {
    if (isEmpty(s)) {
        printf("Stack Underflow\n");
        return -1; // Indicate stack is empty
    }
    return s -> data[(s -> top)--];
}

int main() {
    Stack s;
    initialize(&s);

    push(&s, 10);
    push(&s, 20);
    push(&s, 30);
    printf("%d\n", pop(&s));

}
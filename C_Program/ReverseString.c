#include<stdio.h>
#include<stdlib.h>
#include<string.h>

typedef struct {
    char data[100];
    int top;
} Stack;

void initialize(Stack *s) {
    s->top = -1;
}

void push(Stack *s, char c) {
    if (s->top < 99) {
        s->data[++(s->top)] = c;
    }
}

char pop(Stack *s) {
    if (s->top >= 0) {
        return s->data[(s->top)--];
    }
    return '\0';
}

void reverseString(char str[]) {
    int length = strlen(str);
    Stack s;
    initialize(&s);
    for (int i = 0; i < length; i++) {
        push(&s, str[i]);
    }

    for (int i = 0; i < length; i++) {
        str[i] = pop(&s);
    }
}

int main() {
    char str[] = "Hello, World!";
    printf("Original String: %s\n", str);
    reverseString(str);
    printf("Reversed String: %s\n", str);
    return 0;
}
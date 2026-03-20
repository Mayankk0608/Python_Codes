#include<stdio.h>
#include<stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct {
    Node* top;
} Stack;

void initialize(Stack *s) {
    s->top = NULL;
}

int isEmpty(Stack *s) {
    return s->top == NULL;
}   

void push(Stack *s, int value) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    if (!newNode) {
        printf("Memory allocation failed\n");
        return;
    }
    newNode->data = value;
    newNode->next = s->top;
    s->top = newNode;
}

int pop(Stack *s) {
    if (isEmpty(s)) {
        printf("Stack Underflow\n");
        return -1; // Indicate stack is empty
    }
    Node* temp = s->top;
    int poppedValue = temp->data;
    s->top = s->top->next;
    free(temp);
    return poppedValue;
}

int main() {
    Stack s;
    initialize(&s);

    push(&s, 10);
    push(&s, 20);
    push(&s, 30);
    printf("%d\n", pop(&s));

    return 0;
}
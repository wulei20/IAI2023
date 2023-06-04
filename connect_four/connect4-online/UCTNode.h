#ifndef UCTNODE_H
#define UCTNODE_H

#include "Point.h"

void initStatic(int M, int N, Point noMove, int** board, int* top);
void deleteStatic();

class UCTNode {
public:
    // static variables for basic information of board
    static int M, N;
    static int** board;
    static int* top;
    static Point NoMove;

    // variables for Node
    Point lastMove_;
    bool currentPlayer_;        // false means current player is opponent, true means current player is machine(self)
    int selectableNum_;         // number of selectable columns
    int* selectableColumns_;    // array of selectable columns that not selected
    UCTNode* parent_;           // parent node
    UCTNode** children_;        // array of expanded children, disjoint with selectableColumns_ (when the column is expanded as a child, the column is removed from selectableColumns_)
    int profit_;                // profit of the node, 1 for win, -1 for lose, 0 for draw
    int accessTimes_;           // number of times the node is accessed
    int finish_;                // 0 for not finished, 1 for finished, -1 for not started
    bool expanded_;             // whether the node is expanded

    // functions for Node
    UCTNode(Point lastMove, bool currentPlayer, UCTNode* parent);
    ~UCTNode();

    bool isLeaf();          // whether the node is leaf(the game is over)
    bool Movable();         // whether there is a movable point
    UCTNode* Expand();      // expand a node as a child
    int WinPoint(bool currentPlayer); // return column number of a winning point for currentPlayer, -1 for no winning point


    // functions for UCT
    Point UCTSearch(const int* rootTop, const int** rootBoard);
    // select a node to expand
    UCTNode* TreePolicy();
    // select the best child
    UCTNode* BestChild(bool move);
    // simulate a game from the current state to calculate the profit
    int DefaultPolicy();
    // return the plain profit of current player, 1 for win, -1 for lose, 0 for draw, -2 for not finished
    int getCurrentProfit(bool currentPlayer, Point lastMove);
    // randomly simulate next single step
    void randomStep(bool currentPlayer, Point& lastMove);
    // update the profit of the node and its ancestors
    void BackUp(int delta);
};

const double c = 0.9;
const double TLE = 2.6;

#endif
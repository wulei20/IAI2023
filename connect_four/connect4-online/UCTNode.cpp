#include "UCTNode.h"

#include <cstdlib>
#include <cmath>
#include <sys/time.h>
#include <cstring>
#include <iostream>

#include "Judge.h"

int UCTNode::M, UCTNode::N;
Point UCTNode::NoMove(-1, -1);
int** UCTNode::board;
int* UCTNode::top;

void initStatic(int M, int N, Point noMove, int** board, int* top) {
    UCTNode::M = M;
    UCTNode::N = N;
    UCTNode::NoMove = noMove;
    UCTNode::board = new int*[M];
    for (int i = 0; i < M; i++) {
        UCTNode::board[i] = new int[N];
        memcpy(UCTNode::board[i], board[i], sizeof(int) * N);
    }
    UCTNode::top = new int[N];
    memcpy(UCTNode::top, top, sizeof(int) * N);
}

void deleteStatic() {
    for (int i = 0; i < UCTNode::M; i++) {
        delete[] UCTNode::board[i];
    }
    delete[] UCTNode::board;
    delete[] UCTNode::top;
}

UCTNode::UCTNode(Point lastMove, bool currentPlayer, UCTNode* parent): lastMove_(lastMove), currentPlayer_(currentPlayer),
    selectableNum_(0), parent_(parent), profit_(0), accessTimes_(0), finish_(-1), expanded_(false) {
    this->selectableColumns_ = new int[N];
    this->children_ = new UCTNode*[N];
    for (int i = 0; i < N; i++) {
        if (top[i]) {
            this->selectableColumns_[this->selectableNum_++] = i;
        }
        this->children_[i] = nullptr;
    }
}

UCTNode::~UCTNode() {
    delete[] this->selectableColumns_;
    for (int i = 0; i < N; i++) {
        if (this->children_[i] != nullptr) {
            delete this->children_[i];
        }
    }
    delete[] this->children_;
}

bool UCTNode::isLeaf() {
    if (finish_ != -1) return finish_;
    else if (lastMove_.x == -1 && lastMove_.y == -1) {
        finish_ = 0;
        return false;
    }
    if ((!currentPlayer_ && machineWin(lastMove_.x, lastMove_.y, M, N, board)) || 
    (currentPlayer_ && userWin(lastMove_.x, lastMove_.y, M, N, board))) {
        finish_ = 1;
        return true;
    } else if (isTie(N, top)) {
        finish_ = 1;
        return true;
    } else {
        finish_ = 0;
        return false;
    }
}

bool UCTNode::Movable() {
    return selectableNum_ > 0;
}

UCTNode* UCTNode::Expand() {
    bool nextPlayer = !currentPlayer_;
    Point nextMove(-1, -1);
    if (!expanded_) {
        expanded_ = true;
        if ((nextMove.y = WinPoint(currentPlayer_)) != -1) {
            // winning point that must be placed
            nextMove.x = --top[nextMove.y];
            board[nextMove.x][nextMove.y] = currentPlayer_ ? 2 : 1;
            // maintain top for noMove
            if (NoMove.x == nextMove.x - 1 && NoMove.y == nextMove.y) top[nextMove.y]--;
            selectableNum_ = 0;
            children_[nextMove.y] = new UCTNode(nextMove, nextPlayer, this);
            return children_[nextMove.y];
        } else if ((nextMove.y = WinPoint(nextPlayer)) != -1) {
            // opponent's winning point that must be placed
            nextMove.x = --top[nextMove.y];
            board[nextMove.x][nextMove.y] = nextPlayer ? 2 : 1;
            // maintain top for noMove
            if (NoMove.x == nextMove.x - 1 && nextMove.y) top[nextMove.y]--;
            selectableNum_ = 0;
            children_[nextMove.y] = new UCTNode(nextMove, nextPlayer, this);
            return children_[nextMove.y];
        }
    }
    // select a point by normal rules
    while(true) {
        int select = rand() % selectableNum_;
        nextMove.y = selectableColumns_[select];
        nextMove.x = --top[nextMove.y];
        board[nextMove.x][nextMove.y] = currentPlayer_ ? 2 : 1;
        // remove the selected column from selectableColumns_
        selectableColumns_[select] = selectableColumns_[--selectableNum_];
        // maintain top for noMove
        if (NoMove.x == nextMove.x - 1 && nextMove.y) top[nextMove.y]--;
        // if the opponent can't place upon the selected point, this move will not cause the opponent to win
        // so we can choose this move
        // or if there are no selectable columns, break
        if (!top[nextMove.y] || !selectableNum_) break;
        // if the opponent can win in the next step, discard this move
        // since the only change is the selected point, the opponent can only win by placing a point upon the selected point
        // so we only need to check the point upon the selected point
        board[top[nextMove.y] - 1][nextMove.y] = nextPlayer ? 2 : 1;
        if ((!currentPlayer_ && machineWin(top[nextMove.y] - 1, nextMove.y, M, N, board)) ||
        (currentPlayer_ && userWin(top[nextMove.y] - 1, nextMove.y, M, N, board))) {
            // this move will cause the opponent to win, so we can't choose this move
            board[top[nextMove.y] - 1][nextMove.y] = 0;
            // maintain top for noMove
            if (NoMove.x == top[nextMove.y] && NoMove.y == nextMove.y) top[nextMove.y]++;
            board[nextMove.x][nextMove.y] = 0;
            top[nextMove.y]++;
        } else
            break;
    }
    children_[nextMove.y] = new UCTNode(nextMove, nextPlayer, this);
    return children_[nextMove.y];
}

int UCTNode::getCurrentProfit(bool currentPlayer, Point lastMove) {
    if (!currentPlayer && machineWin(lastMove.x, lastMove.y, M, N, board)) return 1;
    else if (currentPlayer && userWin(lastMove.x, lastMove.y, M, N, board)) return -1;
    else if (isTie(N, top)) return 0;
    else return -2;
}

int UCTNode::WinPoint(bool currentPlayer) {
    for (int i = 0; i < selectableNum_; i++) {
        int y = selectableColumns_[i];
        int x = top[y] - 1;
        // suppose the point is placed
        board[x][y] = currentPlayer ? 2 : 1;
        if ((currentPlayer && machineWin(x, y, M, N, board)) || (!currentPlayer && userWin(x, y, M, N, board))) {
            // reset board
            board[x][y] = 0;
            return y;
        }
        // reset board
        board[x][y] = 0;
    }
    return -1;
}

UCTNode* UCTNode::BestChild(bool move) {
    double max = -1e30;
    Point bestMove(-1, -1);
    UCTNode* bestChild = nullptr;
    for (int i = 0; i < N; i++) {
        if (children_[i] != nullptr) {
            // realChildProfit = profit of the child for the current player
            // if the current player is the opponent, the profit should be reversed
            double realChildProfit = currentPlayer_ ? children_[i]->profit_ : -children_[i]->profit_;
            double value = realChildProfit / children_[i]->accessTimes_ + 
                c * sqrt(2 * log(accessTimes_) / children_[i]->accessTimes_);
            if (value > max) {
                max = value;
                bestChild = children_[i];
                bestMove.y = i;
            }
        }
    }
    if (move) {
        bestMove.x = --top[bestMove.y];
        board[bestMove.x][bestMove.y] = currentPlayer_ ? 2 : 1;
        // maintain top for noMove
        if (NoMove.x == bestMove.x - 1 && NoMove.y == bestMove.y) top[bestMove.y]--;
    }
    return bestChild;
}

void UCTNode::BackUp(int delta) {
    UCTNode* node = this;
    while (node) {
        node->accessTimes_++;
        node->profit_ += delta;
        node = node->parent_;
    }
}

Point UCTNode::UCTSearch(const int* rootTop, const int** rootBoard) {
    timeval start, end;
    gettimeofday(&start, NULL);
    gettimeofday(&end, NULL);
    // initialize random seed
    srand(time(NULL));
    // int simulationTimes = 0;
    // start UCT
    while (end.tv_sec - start.tv_sec + (end.tv_usec - start.tv_usec) / 1000000.0 < TLE) {
        // simulationTimes++;
        // reset the board
        for (int i = 0; i < M; i++) {
            memcpy(board[i], rootBoard[i], sizeof(int) * N);
        }
        // reset top
        memcpy(top, rootTop, sizeof(int) * N);
        UCTNode* node = TreePolicy();
        int delta = node->DefaultPolicy();
        node->BackUp(delta);
        gettimeofday(&end, NULL);
    }
    // std::cerr << "simulationTimes: " << simulationTimes << std::endl;
    // choose the best child
    UCTNode* bestChild = BestChild(false);
    return bestChild->lastMove_;
}

UCTNode* UCTNode::TreePolicy() {
    UCTNode* node = this;
    while (!node->isLeaf()) {
        if (node->Movable()) {
            return node->Expand();
        } else {
            node = node->BestChild(true);
        }
    }
    return node;
}

int UCTNode::DefaultPolicy() {
    bool currentPlayer = currentPlayer_;
    Point lastMove = lastMove_;
    int profit = getCurrentProfit(currentPlayer, lastMove);
    while (profit == -2) {
        randomStep(currentPlayer, lastMove);
        profit = getCurrentProfit(!currentPlayer, lastMove);
        currentPlayer = !currentPlayer;
    }
    return profit;
}

void UCTNode::randomStep(bool currentPlayer, Point& lastMove) {
    while (true) {
        lastMove.y = rand() % N;
        if (top[lastMove.y] > 0) {
            lastMove.x = --top[lastMove.y];
            board[lastMove.x][lastMove.y] = currentPlayer ? 2 : 1;
            // maintain top for noMove
            if (NoMove.x == lastMove.x - 1 && NoMove.y == lastMove.y) top[lastMove.y]--;
            break;
        }
    }
}
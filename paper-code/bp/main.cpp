
#define _CRT_SECURE_NO_WARNINGS 1

#include <math.h>
#include <ctype.h>
#include <fstream>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <vector>
#include <time.h>

using namespace std;

const int MaxBaseSize = 1500;
const bool PRINTROWS = true;
int numx = 0;
int NumInputs;
int NumTargets;
int ProgramSize;
long long int Target[MaxBaseSize];
int Dist[MaxBaseSize]; //distance from current base to Target[i]
int NDist[MaxBaseSize]; //what Dist would be if NewBase was added
long long int Base[MaxBaseSize];
int BaseSize;
int TargetsFound;
long long int LastBase1, LastBase2;

void InitBase();
void ReadTargetMatrix();
bool is_target(long long int x);
bool is_base(long long int x);
int NewDistance(int u); //calculates the distance from the base to Target[u]
int TotalDistance(); //returns the sum of distances to targets
bool reachable(long long int T, int K, int S);
bool EasyMove(); //if any two bases add up to a target, pick them
void PickNewBaseElement();
void binprint(long long int x); //outputs last NumInputs bits of x 
void init_FP();
struct FP{
    int a[1500],b[1500],c[1500];
    int ans=0;
}p;
ifstream TheMatrix;
//ofstream out_file;

FILE* pp;


int main(int argc, char* argv[])
{
    int NumMatrices;
    pp = fopen("result.txt", "w");
    clock_t t1 = clock();
    TheMatrix.open("example.txt");
    TheMatrix >> NumMatrices;
    fprintf(pp, "%d\n", NumMatrices);
    double ans=0;
    int sun=2;
    vector<int> aa;
    for (int i = 0; i < NumMatrices; i++)
    {
        init_FP();
        ReadTargetMatrix();
        InitBase();
        ProgramSize = 0;
        int counter = 0;
        while (TargetsFound < NumTargets)
        {
            counter++;
            if (!EasyMove()) PickNewBaseElement();
        }
        
        fprintf(pp, "%d\n", p.ans);
        for (int k = 0; k < p.ans; k++)
            fprintf(pp, "%d %d %d\n", p.a[k], p.b[k], p.c[k]);
        printf("matrix %d: %d XOR gates\n", i + 1, ProgramSize);
    }
    clock_t t2 = clock();
    cout << (t2 - t1) / (double)CLOCKS_PER_SEC;
}//main

void init_FP(){
    for(int i=0;i<1500;i++){
        p.a[i]=0,p.b[i]=0,p.c[i]=0;
    } p.ans=0;
}

void InitBase()
{
    TargetsFound = 0;
    Base[0] = 1;
    for (int i = 1; i < NumInputs; i++) Base[i] = 2 * Base[i - 1];
    BaseSize = NumInputs; //initial base is just the xi's
    for (int i = 0; i < NumTargets; i++)
        if (Dist[i] == 0) TargetsFound++;
}


long long int NewBase; //global variable containing a candidate new base

bool EasyMove()
{
    int t;
    bool foundone = false;

    // see if anything in the distance vector is 1
    for (int i = 0; i < NumTargets; i++)
        if (Dist[i] == 1)
        {
            foundone = true;
            t = i;
            break;
        }
    if (!foundone) return false;
    // update Dist array
    NewBase = Target[t];
    for (int u = 0; u < NumTargets; u++) Dist[u] = NewDistance(u);
    // update Base with NewBase 
    Base[BaseSize] = NewBase;
    BaseSize++;
    ProgramSize++;
    TargetsFound++;
    for (int i = 0; i < BaseSize - 1; i++)
    {
        for (int j = i + 1; j < BaseSize; j++)
        {
            if ((Base[i] ^ Base[j]) == NewBase)
            {
                LastBase1 = Base[i];
                LastBase2 = Base[j];
                //cout <<  BaseSize - 1  <<" "<< i <<  " " << j << endl;
                p.a[p.ans]=BaseSize - 1,p.b[p.ans]=i,p.c[p.ans]=j;
                p.ans++;
                //fprintf(pp, "%d %d %d\n", BaseSize - 1, i, j);
                return true;
            }
        }
    }
    return true;
} // EasyMove()

int NewDistance(int u, long long int newBaseVal) {
    if (is_base(Target[u]) || (newBaseVal == Target[u])) return 0;
    if (reachable(Target[u] ^ newBaseVal, Dist[u] - 1, 0)) return (Dist[u] - 1);
    else return Dist[u];
}

int TotalDistance(long long int newBaseVal, int* resultNDist) {
    int D = 0;
    for (int i = 0; i < NumTargets; i++) {
        int t = NewDistance(i, newBaseVal);
        if (resultNDist != nullptr) {
            resultNDist[i] = t;
        }
        D += t;
    }
    return D;
}

void PickNewBaseElement() {
    int MinDistance = BaseSize * NumTargets;
    int OldNorm = 0;
    long long int TheBest = 0;
    int besti = -1, bestj = -1;
    int* BestDist = new int[NumTargets];

#pragma omp parallel
    {
        int localMinDistance = MinDistance;
        int localOldNorm = OldNorm;
        long long int localTheBest = TheBest;
        int localBesti = besti, localBestj = bestj;
        int* localBestDist = new int[NumTargets];

#pragma omp for nowait
        for (int i = 0; i < BaseSize - 1; i++) {
            for (int j = i + 1; j < BaseSize; j++) {
                long long int newBaseVal = Base[i] ^ Base[j];
                if (newBaseVal == 0) continue;
                if (is_base(newBaseVal)) continue;
                if (is_target(newBaseVal)) {
#pragma omp critical
                    {
                        cout << "shouldn't find an easy target here " << endl;
                        exit(0);
                    }
                }

                int* localNDist = new int[NumTargets];
                int ThisDist = TotalDistance(newBaseVal, localNDist);
                int ThisNorm = 0;
                for (int k = 0; k < NumTargets; k++) {
                    int d = localNDist[k];
                    ThisNorm += d * d;
                }

                bool update = false;
                if (ThisDist < localMinDistance) {
                    update = true;
                }
                else if (ThisDist == localMinDistance && ThisNorm > localOldNorm) {
                    update = true;
                }

                if (update) {
                    localMinDistance = ThisDist;
                    localOldNorm = ThisNorm;
                    localTheBest = newBaseVal;
                    localBesti = i;
                    localBestj = j;
                    for (int k = 0; k < NumTargets; k++) {
                        localBestDist[k] = localNDist[k];
                    }
                }
                delete[] localNDist;
            }
        }

#pragma omp critical
        {
            if (localMinDistance < MinDistance ||
                (localMinDistance == MinDistance && localOldNorm > OldNorm)) {
                MinDistance = localMinDistance;
                OldNorm = localOldNorm;
                TheBest = localTheBest;
                besti = localBesti;
                bestj = localBestj;
                for (int k = 0; k < NumTargets; k++) {
                    BestDist[k] = localBestDist[k];
                }
            }
        }
        delete[] localBestDist;
    }

    if (besti == -1 || bestj == -1) {
        cout << "Error: no valid pair found!" << endl;
        exit(1);
    }

    LastBase1 = Base[besti];
    LastBase2 = Base[bestj];
    //cout <<  BaseSize << " " <<  besti << " " << bestj << endl;
    p.a[p.ans]=BaseSize,p.b[p.ans]=besti,p.c[p.ans]=bestj;
    p.ans++;
    //fprintf(pp, "%d %d %d\n", BaseSize, besti, bestj);

    for (int i = 0; i < NumTargets; i++) {
        Dist[i] = BestDist[i];
    }

    Base[BaseSize] = TheBest;
    BaseSize++;
    ProgramSize++;

    delete[] BestDist;
}


void binprint(long long int x) //outputs last NumInputs bits of x 
{
    long long int t = x;
    for (int i = 0; i < NumInputs; i++)
    {
        if (t % 2) cout << "1 "; else cout << "0 ";
        t = t / 2;
    }
} //binprint  

void ReadTargetMatrix()
{
    TheMatrix >> NumTargets;
    TheMatrix >> NumInputs;
    //check that NumInputs is < wordsize
    if (NumInputs >= 8 * sizeof(long long int))
    {
        cout << "too many inputs" << endl;
        exit(0);
    }

    int bit;
    for (int i = 0; i < NumTargets; i++)
        //read row i
    {
        long long int PowerOfTwo = 1;
        Target[i] = 0;
        Dist[i] = -1; //initial distance from Target[i] is Hamming weight - 1
        for (int j = 0; j < NumInputs; j++)
        {
            TheMatrix >> bit;
            if (bit)
            {
                Dist[i]++;
                Target[i] = Target[i] + PowerOfTwo;
            }
            PowerOfTwo = PowerOfTwo * 2;
        }
    }
} //ReadTargetMatrix()


bool is_target(long long int x)
{
    for (int i = 0; i < NumTargets; i++)
        if (x == Target[i]) return true;
    return false;
} //is_target

bool is_base(long long int x)
{
    //sanity check, shouldn't ask if 0 is base
    if (x == 0) { cout << "asking if 0 is in Base " << endl; exit(0); }

    for (int i = 0; i < BaseSize; i++) if (x == Base[i]) return true;
    return false;
} //is_base

// Distance is 1 less than the number of elements
// in the base that I need to add in order to get Target[u].
// The next function calculates the distance from the base,
// augmented by NewBase, to Target[u]. Uses the following observations:
// Adding to the base can only decrease distance. 
// Also, since NewBase is the sum of two old base 
// elements, the distance from the augmented base 
// to Target[u] can decrease at most by 1. If the
// the distance decreases, then NewBase must be one
// of the summands.

int NewDistance(int u)
{
    //if Target[u] is in augmented base return 0;
    if (is_base(Target[u]) || (NewBase == Target[u])) return 0;

    // Try all combinations of Dist[u]-1 base elements until one sums 
    // to Target[u] + NewBase. If this is true, then Target[u] is the
    // sum of Dist[u] elements in the augmented base, and therefore
    // the distance decreases by 1.

    if (reachable(Target[u] ^ NewBase, Dist[u] - 1, 0)) return (Dist[u] - 1);
    else return Dist[u]; //keep old distance 
} //NewDistance(int u) 


//return true if T is the sum of K elements among Base[S..BaseSize-1]
bool reachable(long long int T, int K, int S)
{
    if ((BaseSize - S) < K) return false; //not enough base elements

    if (K == 0) return false; //this is probably not reached
    if (K == 1)
    {
        for (int i = S; i < BaseSize; i++) if (T == Base[i]) return true;
        return false;
    }

    //consider those sums containing Base[S]
    if (reachable(T ^ Base[S], K - 1, S + 1)) return true;
    //consider those sums not containing Base[S]
    if (reachable(T, K, S + 1)) return true;
    //not found
    return false;
} // reachable(long long int T, int K, int S)

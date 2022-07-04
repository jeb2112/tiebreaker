---
layout: default
title: Math
permalink: /math/
---
The math for this app turned up a few interesting tidbits. 

To begin with, for the standard 4 team round robin of 3 games per team, there are a total of 6 games. In a cross-matrix of games played, the upper triangular entries can randomly be any one of a Win, Loss or Tie, while the lower triangular entries are then dependent on the upper triangular:

 | Team | Chiefs | team X | team A | Bots | 
    | ---- | ----- | ---- | ------ | ---- |
    | Chiefs | -   | WLT    | WLT      | WLT    |
    | team X    |      | -    | WLT      | WLT    |
    | team A    |      |     | -      | WLT    |
    | Bots |      |     |       | -    |

If a Win is worth 2 points and a Tie 1 point, then the set of possible points outcomes in the upper triangular 6 games is drawn from the set $$[0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]$$, and the total number of possible combinations is $$C(18,6) = 18564$$.

These point outcomes resolve to just 12 unique sets of points for the final round robin standings:

|1st|2nd|3rd|4th|
    |---|---|---|---|
    |4| 4| 2| 2|
    | 6| 5| 1| 0|
    | 5| 5| 1| 1|
    | 5| 4| 3| 0|
    | 3| 3| 3| 3|
    | 4| 4| 3| 1|
    | 5| 5| 2| 0|
    | 6| 3| 3| 0|
    | 6| 4| 2| 0|
    | 6| 6| 0| 0|
    | 4| 3| 3| 2|
    | 5| 4| 2| 1 |

From this list it can be seen that there are three cases in which there is a tie for 2nd and 3rd place. The total number of instances of each of these three cases can be tallied as a sub-total of 18564. Note that only instances in which the 2nd place finisher also tied the 3rd place finisher in their head-to-head game require the tie-breaker formula and so are counted here:

|1st|2nd|3rd|4th|n|incidence (%)|
    |---|---|---|---|-|-|
    | 6| 3| 3| 0|360|1.94|
    | 4| 3| 3| 2|48|0.26|
    | 3| 3| 3| 3|1|.0054|

So overall there is a 2.2% chance that any round robin will end up requiring a tie-breaker according to a goals ratio formula. Note that the (3,3,3,3) case corresponds to all 6 games ending as Ties, and this one scenario is not covered in the current version of the app. Note also that while I have focused on the question of qualification for further play between the 2nd and 3rd place finishers in the instructions to this app, the same goals ratio formula may also be used to break a tie between 1st and 2nd place finishers for purposes of assigning seeds in the elimination bracket of the tournament. 

The tie-break statistic is:

$$\frac{\sum_{i=1}^N GF_i}{\sum_{i=1}^N (GF_i+GA_i)}, N = \text{number of games}$$

Let $$x,y$$ be the numbers of goals for and against for team X in the final game of the round robin. Then in order for team X to qualify over team A in an $$N=3$$ round robin, it is required that:

$$\frac{x + \sum_{i=1}^2 GF_{X,i}}{x + y + \sum_{i=1}^2 (GF_{X,i}+GA_{X,i})} > \frac{\sum_{i=1}^3 GF_{A,i}}{\sum_{i=1}^3 (GF_{A,i}+GA_{A,i})}$$

which for the numerical example in the Instructions reduces to: 

$$x - y + 3 > 0 $$

where $$x,y>=0$$ and are integers. It is straightforward to evaluate this equation for a range of $$0<=x,y<=10$$ say and plot the results as seen in the app, but I did also make a quick attempt to see if there were any mathematical formulations of the problem.

I began with the simpler case of equality, which corresponds to any yellow-coloured results in the various output plots.

$$x - y  = -3 $$

or more generally,

$$ ax + by = c $$

As it turns out, this is an example of a linear Diophantine equation, a term I had never heard before. But in fact the famous Pythagorean equation is a 2nd order Diophantine in 3 variables when constrained to be integer, and higher order versions of that equation are the subject of none other than Fermat's Last Theorem, which was only proved in 1995. I didn't have to dig very deep to come up with these little factoids on wikipedia, and I'm amazed I can go from minor hockey in the GTHL to Fermat's Last theorem in just three degrees of separation.

The linear Diophantine equation has a solution according to the following theorem:

```
The equation ax+by=c has a solution (where x and y are integers) if and only if c 
is a multiple of the greatest common divisor of a and b.
```
and since -3 is a multiple of 1, therefore the numerical example does have a (at least one) solution. For the general case of equality, I found that python has a diophantine solver in the symbolic math package so just for the heck of it I used that. 

As for the much larger case of inequality, that was more problematic. Inequality doesn't seem to be included in Diophantine analysis, and the restriction to integer solutions eliminates certain other types of analysis. I'm not any sort of mathematician, and carried this no further. The inequalities were solved by simple evaluation.   

---
layout: default
title: Instructions
permalink: /instructions/
---
1. Consider the following hypothetical table of standings in a four team round robin. The Chiefs have qualified to advance, in first place. Team A has also completed 3 games of the round robin. Team X has completed 2 games and has 1 final game remaining against the Bots. Finally, team X tied team A in their head-to-head game:

    | Team | Games | Wins | Losses | Ties | points |
    | ---- | ----- | ---- | ------ | ---- | ------ |
    | Chiefs | 3   | 3    | 0      | 0    | 6      |
    | X    | 2     | 1    | 0      | 1    | 3      |
    | A    | 3     | 1    | 1      | 1    | 3      |
    | Bots | 2     | 0    | 2      | 0    | 0      |

    *If team X loses the final game, there will be a tie with team A in the final round robin standings, and the tie-breaker formula will be needed to resolve it.*

2. The tie breaking formula used by many tournament organizations is that the team with the higher ratio of $$\frac{\sum_{i=1}^N GF_i}{\sum_{i=1}^N (GF_i+GA_i)}$$ qualifies to advance, where $$GF_i,GA_i$$ are the goals for and against in the $$i'th$$ game, and $$N$$ is the number of games played in the round robin. For a four team round robin, $$N$$ is usually 3 as depicted in this example.

3. Enter the total goals (for and against) for teams A and X, pending team X's final game, and then press return.

    ![step 1]({{site.baseurl}}/images/tb_instructions_1.png "Step 1")

    *Team A has scored 12 for and given up 12 against during their 3 games. Team X has scored 13 and given up 10 in their 2 games so far.*

4. The goal scoring scenarios in the final game required for Team X to qualify are plotted as a matrix.

    ![step 2]({{site.baseurl}}/images/tb_instructions_2.png "Step 2")

    *Read across the bottom axis for goals against. Read the left vertical axis to see the goals for.*
5. Any green square shows a GA,GF pair (ie a game score) that combines with the totals from their first two games and qualifies team X for further play.

    ![step 3]({{site.baseurl}}/images/tb_instructions_3.png "Step 3")

    *The black 'x' indicates a scenario in which team X lost 4-3 in their final game, but qualify ahead of team A for further play based on the total goals ratio.*
6. The yellow squares (if any) denote (GA,GF) pairs that fail to break the tie, according to the formula.

    ![step 4]({{site.baseurl}}/images/tb_instructions_4.png "Step 4")

    *The black 'x' indicates a scenario in which team X lost 5-2 in their final game, and are still tied with team A based on overall goals ratio. Tournament organizers will go to a second tie-breaking rule, which is then beyond the scope of this app.*
7. Note that matrix output shows both Win ($$GF>GA$$) and Loss ($$GA>GF$$) scenarios for team X in game 3, whereas it is only a Loss for team X that will lead to a Tie in the round robin standings, in this fictitious example. And in general, for any round robin scenario it is known in advance of game 3 whether it is a Win or Loss that leads to a Tie in the final standings.
8. To select alternate outputs showing only the known Win/Loss scenario, use the 'output' menu.

    ![step 5]({{site.baseurl}}/images/tb_instructions_5.png "Step 5")

    *Select \'bar\' or \'tabular\' for Win- or Loss-only scenarios. This will activate the radio buttons. To select Win or Loss scenarios use the \'W\' and \'L\' radio buttons respectively.*

9. The bar chart displays a modified vertical axis showing the net difference $$GF-GA$$. If the 'L' radio button is clicked to switch to the Loss scenario, the bar chart is plotted like this:

    ![step 7]({{site.baseurl}}/images/tb_instructions_7.png "Step 7")

    *In this Loss scenario, GF < GA so the vertical axis is negative. The plot shows that for GA of 0,1 or 2, team X will qualify regardless of goals for. If the GA >= 3, then team X will qualify if they lose by no more than 2 goals, and they will still be tied with team A if they lose by no more than 3 goals. If the GA >=4, team X will fail to qualify if they lose by 4 goals or more.*

10. For both Win and Loss scenarios, a data point for $$GF-GA=0$$ is plotted. Obviously this is a tie and not a win or a loss. Nevertheless, this data point is included to include one point of continuity between the separate Win and Loss plots.

11. If the 'tabular' output is selected, then the same data are written out in a table. If there are more than four rows in the table, the table can be scrolled.

    ![step 8]({{site.baseurl}}/images/tb_instructions_8.png "Step 8")

    *For the same Loss scenario as in step 9, the several GA scenarios are tabulated. There are exactly four rows, so the table is not scrollable. In essence, the table simply lists what is written in english in the caption of step 9. However note that some of the information displayed in the bar chart is not explicitly shown in the table. In other words, the table shows at most one result for each value of GA, but sometimes only one result for a range of GA, whichever is the most concise way to communicate the results. Furthermore, by default the limiting GF-GA case for team X to qualify is shown with a green background, rather than the nearest GF-GA case that would disqualify team X (ie with a red background). However, where there is no qualification possible for a given GA value, then the GF-GA result that disqualifies team X will be shown with a red background. Thirdly, where a Tie outcome is present for a given GA value, the GF-GA will be tallied in the table with a yellow background, and the limiting case for team X to qualify must then be inferred. So for example in this table, for any GA > 2, team X will still be tied with team A if they lose by 3 goals. From this it can be inferred that team X will qualify if they lose by 2 goals or less.*

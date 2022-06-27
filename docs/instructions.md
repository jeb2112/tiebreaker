---
layout: default
title: Instructions
permalink: /instructions/
---
1. Team A has completed all 3 games of the round robin, while Team X has completed 2 games.
2. Enter the total goals (for and against) for both teams, then press return.
![step 1](/images/tb_instructions_1.png "Step 1")

    *Team A has scored 12 for and given up 12 against during their 3 games. Team X has scored 13 and given up 10 in just 2 games.*
3. The goal scoring scenarios in the 3rd and final game required for Team X to qualify are plotted as a matrix.

    ![step 2](/images/tb_instructions_2.png "Step 2")

    *Read across the bottom axis for goals against. Read the left vertical axis to see the goals for.*
4. Any green square shows a goals-against,goals-for pair (GA,GF) that qualifies team X for further play.

    ![step 3](/images/tb_instructions_3.png "Step 3")

    *The black 'x' indicates a scenario in which team X scored a 3-2 victory in their final game, and qualify for further play based on overall GF/(GF+GA) ratio*
5. The yellow squares (if any) denote (GA,GF) pairs that fail to break the tie, according to the current formula.

    ![step 4](/images/tb_instructions_4.png "Step 4")

    *The black 'x' indicates a scenario in which team X lost 5-2 in their final game, and are still tied with team A based on overall GF/(GF+GA) ratio*
6. Note that matrix output shows both Win (GF>GA) and Loss (GA>GF) scenarios for team X in game 3, whereas only one or the other of those outcomes actually leads to a Tie with team A in the round robin standings.
7. To select alternate outputs showing the known Win/Loss scenario, use the 'output' menu.

    ![step 5](/images/tb_instructions_5.png "Step 5")

    *Select \'bar\' or \'tabular\' for Win- or Loss-only scenarios. This will activate the radio buttons. To select Win or Loss scenarios use the \'W\' and \'L\' radio buttons respectively.*

8. The bar chart displays a modified vertical axis showing the net difference GF-GA. 

    ![step 6](/images/tb_instructions_6.png "Step 6")

    *In a Win scenario, GF > GA so the vertical axis is positive. The plot shows that team X qualifies for any GA scenario, regardless of GF. Note that the vertical axis begins at 0, which is actually a tie. The zero (0) GF is plotted for both Win and Loss scenarios to establish a continuity between the two plots.*
9. If the 'L' radio button is clicked to switch to the Loss scenario, the bar chart is replotted accordingly.

    ![step 7](/images/tb_instructions_7.png "Step 7")

    *In this Loss scenario, GF < GA so the vertical axis is negative. The plot shows that for GA of 0,1 or 2, team X will qualify. If the GA >= 3, then team X will qualify if they lose by no more than 2 goals, and they will still be tied with team A if they lose by no more than 3 goals. If the GA >=4, team X will fail to qualify if they lose by 4 goals or more.*
10. If the 'tabular' output is selected, then the same data are written out in a table. If there are more than four rows in the table, the table can be scrolled.

    ![step 8](/images/tb_instructions_8.png "Step 8")

    *For the same Loss scenario as in step 9, the several GA scenarios are tabulated. There are exactly four rows, so the table is not scrollable. In essence, the table simply lists what is written in the caption above. However note that some of the information displayed in the bar chart is not explicitly shown in the table. In other words, the table shows at most one result for each value of GA. Therefore the limiting green scenario for qualify is shown, and the nearest red for disqualify is never shown. Likewise, where a yellow Tie outcome is present for a given GA, that will be tallied in the table, and the matching green qualify outcome must then be inferred.*

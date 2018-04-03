# CodinGame Python Arena

CodinGame.com is a coding competition site.  There are a number of
compititions where players can code bots and play them against others.
This is a testing enviroment where one can test different versions
of their Python3 bots against one another.

_Note: This arena is implemented for CodinGame's Wondev Women
competition but can be modified to accomodate any competition.  One
only needs to adjust the code under `cg_arena/game`.  See the README
file there._

## Usage

### Basic usage (Wondev Women, 10 games)

To use the program as is, download it and from this directory run:

`python3 cg_arena <bot1> <bot2>`

where ``<bot1>`` and ``<bot2>`` are paths of the Python scripts you want to compete
against each other.  By default it will play ten games against each other.

### Other competitions

To use this program on any of the other CodinGame competitions,
you have to modify the code under `cg_arena/game`.  I've provided an
API to make it easier.  See the README file `cg_arena/game/README.md`.

### Longer tournaments
For more (or less than 10 games), you can use the command line argument `-n`.
For example,

`python3 cg_arena <bot1> <bot2> -n 1000`

would play 1000 games.


## Examples

I've provided three example scripts, which are each a very
slight modification of the default code stub on CG.
 - `examples/ww/default.py`: The default code stub on CodinGame.
 - `examples/ww/simple.py`: Plays the first available move.
 - `examples/ww/random_move.py`: Plays a random available move.

We can test the last two examples with

`python3 cg_arena examples/ww/simple.py examples/ww/random_move.py -n 1000`

Here are the final results:
```
Tournament Results 1000/1000 games:
examples/ww/simple.py : 709 [512] wins
    2 player games:  1. 709 [512]  2. 291 [ 94]
examples/ww/random_move.py : 291 [94] wins
    2 player games:  1. 291 [ 94]  2. 709 [512]
Games where results differ: (2, 3) (6, 7) (8, 9) (10, 11) (12, 13) (20, 21) (22, 23) (30, 31) (36, 37) (38, 39) (40, 41) (42, 43) (44, 45) (50, 51) (52, 53) (54, 55) (56, 57) (58, 59) (60, 61) (62, 63) (66, 67) (68, 69) (70, 71) (74, 75) (78, 79) (80, 81) (84, 85) (86, 87) (88, 89) (90, 91) (92, 93) (94, 95) (96, 97) (98, 99) (100, 101) (102, 103) (104, 105) (106, 107) (108, 109) (110, 111) (116, 117) (118, 119) (120, 121) (128, 129) (134, 135) (138, 139) (140, 141) (142, 143) (146, 147) (148, 149) (152, 153) (154, 155) (156, 157) (158, 159) (162, 163) (164, 165) (168, 169) (180, 181) (182, 183) (184, 185) (186, 187) (188, 189) (190, 191) (194, 195) (196, 197) (198, 199) (200, 201) (206, 207) (210, 211) (214, 215) (224, 225) (230, 231) (232, 233) (234, 235) (236, 237) (242, 243) (244, 245) (254, 255) (256, 257) (258, 259) (260, 261) (264, 265) (266, 267) (268, 269) (270, 271) (272, 273) (274, 275) (276, 277) (278, 279) (280, 281) (282, 283) (288, 289) (290, 291) (292, 293) (294, 295) (296, 297) (298, 299) (304, 305) (306, 307) (308, 309) (310, 311) (312, 313) (314, 315) (316, 317) (318, 319) (320, 321) (326, 327) (330, 331) (332, 333) (334, 335) (336, 337) (340, 341) (344, 345) (346, 347) (348, 349) (350, 351) (352, 353) (356, 357) (358, 359) (362, 363) (364, 365) (368, 369) (376, 377) (380, 381) (382, 383) (384, 385) (388, 389) (390, 391) (392, 393) (396, 397) (400, 401) (404, 405) (410, 411) (416, 417) (418, 419) (420, 421) (422, 423) (424, 425) (426, 427) (436, 437) (438, 439) (446, 447) (452, 453) (454, 455) (458, 459) (460, 461) (462, 463) (468, 469) (470, 471) (472, 473) (474, 475) (476, 477) (480, 481) (482, 483) (490, 491) (492, 493) (496, 497) (508, 509) (510, 511) (514, 515) (518, 519) (520, 521) (522, 523) (524, 525) (528, 529) (534, 535) (538, 539) (542, 543) (544, 545) (548, 549) (550, 551) (556, 557) (558, 559) (560, 561) (564, 565) (566, 567) (572, 573) (574, 575) (576, 577) (578, 579) (580, 581) (584, 585) (586, 587) (590, 591) (592, 593) (594, 595) (602, 603) (604, 605) (606, 607) (608, 609) (618, 619) (620, 621) (622, 623) (628, 629) (630, 631) (634, 635) (636, 637) (638, 639) (640, 641) (642, 643) (646, 647) (648, 649) (654, 655) (656, 657) (660, 661) (662, 663) (666, 667) (668, 669) (670, 671) (674, 675) (676, 677) (678, 679) (680, 681) (686, 687) (694, 695) (696, 697) (700, 701) (704, 705) (706, 707) (708, 709) (712, 713) (716, 717) (718, 719) (720, 721) (722, 723) (728, 729) (730, 731) (734, 735) (736, 737) (742, 743) (744, 745) (746, 747) (748, 749) (750, 751) (756, 757) (762, 763) (764, 765) (766, 767) (768, 769) (774, 775) (776, 777) (782, 783) (786, 787) (790, 791) (792, 793) (802, 803) (804, 805) (806, 807) (812, 813) (818, 819) (820, 821) (828, 829) (830, 831) (832, 833) (838, 839) (840, 841) (842, 843) (844, 845) (848, 849) (850, 851) (852, 853) (854, 855) (856, 857) (858, 859) (860, 861) (866, 867) (870, 871) (886, 887) (888, 889) (892, 893) (894, 895) (902, 903) (904, 905) (912, 913) (914, 915) (916, 917) (918, 919) (922, 923) (926, 927) (932, 933) (936, 937) (938, 939) (940, 941) (942, 943) (944, 945) (950, 951) (954, 955) (956, 957) (958, 959) (960, 961) (964, 965) (970, 971) (976, 977) (978, 979) (980, 981) (982, 983) (984, 985) (986, 987) (988, 989) (990, 991) (992, 993) (994, 995) (996, 997)
Total tournament time: 1560.7167777260183 sec
```

This means
- We played 1000 games.
- Every pair of games was the same random starting configuration,
  except the bots were switched.
- The `simple.py` bot won 709 games, 512 of which were games where it
  won the same board configuration in *both* positions.
- The `random_move.py` bot won 291 games, 94 of which were games where it
  won the same board configuration in *both* positions.

The `simple.py` is clearly the winner here!

(The "Games where results differ" can sometimes be useful by giving us the
ability to look at the games where one bot wins in both positions.)
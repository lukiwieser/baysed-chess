import chess
import chess.engine

from chesspp.i_strategy import IStrategy

# Scoring based on PeSTO (Piece-Square Tables Only) Evaluation Functions
# https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function



PAWN   = 0
KNIGHT = 1
BISHOP = 2
ROOK   = 3
QUEEN  = 4
KING   = 5

# board representation
WHITE  = 0
BLACK  = 1

WHITE_PAWN      = (2*PAWN   + WHITE)
BLACK_PAWN      = (2*PAWN   + BLACK)
WHITE_KNIGHT    = (2*KNIGHT + WHITE)
BLACK_KNIGHT    = (2*KNIGHT + BLACK)
WHITE_BISHOP    = (2*BISHOP + WHITE)
BLACK_BISHOP    = (2*BISHOP + BLACK)
WHITE_ROOK      = (2*ROOK   + WHITE)
BLACK_ROOK      = (2*ROOK   + BLACK)
WHITE_QUEEN     = (2*QUEEN  + WHITE)
BLACK_QUEEN     = (2*QUEEN  + BLACK)
WHITE_KING      = (2*KING   + WHITE)
BLACK_KING      = (2*KING   + BLACK)
EMPTY           = (BLACK_KING  +  1)

mg_value = [82, 337, 365, 477, 1025,  0]
eg_value = [94, 281, 297, 512,  936,  0]


FLIP = lambda sq: (sq^56)
OTHER = lambda side: (side^1)


mg_pawn_table = [
      0,   0,   0,   0,   0,   0,  0,   0,
     98, 134,  61,  95,  68, 126, 34, -11,
     -6,   7,  26,  31,  65,  56, 25, -20,
    -14,  13,   6,  21,  23,  12, 17, -23,
    -27,  -2,  -5,  12,  17,   6, 10, -25,
    -26,  -4,  -4, -10,   3,   3, 33, -12,
    -35,  -1, -20, -23, -15,  24, 38, -22,
      0,   0,   0,   0,   0,   0,  0,   0,
]

eg_pawn_table = [
      0,   0,   0,   0,   0,   0,   0,   0,
    178, 173, 158, 134, 147, 132, 165, 187,
     94, 100,  85,  67,  56,  53,  82,  84,
     32,  24,  13,   5,  -2,   4,  17,  17,
     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
      4,   7,  -6,   1,   0,  -5,  -1,  -8,
     13,   8,   8,  10,  13,   0,   2,  -7,
      0,   0,   0,   0,   0,   0,   0,   0,
]

mg_knight_table = [
    -167, -89, -34, -49,  61, -97, -15, -107,
     -73, -41,  72,  36,  23,  62,   7,  -17,
     -47,  60,  37,  65,  84, 129,  73,   44,
      -9,  17,  19,  53,  37,  69,  18,   22,
     -13,   4,  16,  13,  28,  19,  21,   -8,
     -23,  -9,  12,  10,  19,  17,  25,  -16,
     -29, -53, -12,  -3,  -1,  18, -14,  -19,
    -105, -21, -58, -33, -17, -28, -19,  -23,
]

eg_knight_table = [
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25,  -8, -25,  -2,  -9, -25, -24, -52,
    -24, -20,  10,   9,  -1,  -9, -19, -41,
    -17,   3,  22,  22,  22,  11,   8, -18,
    -18,  -6,  16,  25,  16,  17,   4, -18,
    -23,  -3,  -1,  15,  10,  -3, -20, -22,
    -42, -20, -10,  -5,  -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64,
]

mg_bishop_table = [
    -29,   4, -82, -37, -25, -42,   7,  -8,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -16,  37,  43,  40,  35,  50,  37,  -2,
     -4,   5,  19,  50,  37,  37,   7,  -2,
     -6,  13,  13,  26,  34,  12,  10,   4,
      0,  15,  15,  15,  14,  27,  18,  10,
      4,  15,  16,   0,   7,  21,  33,   1,
    -33,  -3, -14, -21, -13, -12, -39, -21,
]

eg_bishop_table = [
    -14, -21, -11,  -8, -7,  -9, -17, -24,
     -8,  -4,   7, -12, -3, -13,  -4, -14,
      2,  -8,   0,  -1, -2,   6,   0,   4,
     -3,   9,  12,   9, 14,  10,   3,   2,
     -6,   3,  13,  19,  7,  10,  -3,  -9,
    -12,  -3,   8,  10, 13,   3,  -7, -15,
    -14, -18,  -7,  -1,  4,  -9, -15, -27,
    -23,  -9, -23,  -5, -9, -16,  -5, -17,
]

mg_rook_table = [
     32,  42,  32,  51, 63,  9,  31,  43,
     27,  32,  58,  62, 80, 67,  26,  44,
     -5,  19,  26,  36, 17, 45,  61,  16,
    -24, -11,   7,  26, 24, 35,  -8, -20,
    -36, -26, -12,  -1,  9, -7,   6, -23,
    -45, -25, -16, -17,  3,  0,  -5, -33,
    -44, -16, -20,  -9, -1, 11,  -6, -71,
    -19, -13,   1,  17, 16,  7, -37, -26,
]

eg_rook_table = [
    13, 10, 18, 15, 12,  12,   8,   5,
    11, 13, 13, 11, -3,   3,   8,   3,
     7,  7,  7,  5,  4,  -3,  -5,  -3,
     4,  3, 13,  1,  2,   1,  -1,   2,
     3,  5,  8,  4, -5,  -6,  -8, -11,
    -4,  0, -5, -1, -7, -12,  -8, -16,
    -6, -6,  0,  2, -9,  -9, -11,  -3,
    -9,  2,  3, -1, -5, -13,   4, -20,
]

mg_queen_table = [
    -28,   0,  29,  12,  59,  44,  43,  45,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
     -1, -18,  -9,  10, -15, -25, -31, -50,
]

eg_queen_table = [
     -9,  22,  22,  27,  27,  19,  10,  20,
    -17,  20,  32,  41,  58,  25,  30,   0,
    -20,   6,   9,  49,  47,  35,  19,   9,
      3,  22,  24,  45,  57,  40,  57,  36,
    -18,  28,  19,  47,  31,  34,  39,  23,
    -16, -27,  15,   6,   9,  17,  10,   5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43,  -5, -32, -20, -41,
]

mg_king_table = [
    -65,  23,  16, -15, -56, -34,   2,  13,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
     -9,  24,   2, -16, -20,   6,  22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -15,  36,  12, -54,   8, -28,  24,  14,
]

eg_king_table = [
    -74, -35, -18, -18, -11,  15,   4, -17,
    -12,  17,  14,  17,  17,  38,  23,  11,
     10,  17,  23,  15,  20,  45,  44,  13,
     -8,  22,  24,  27,  26,  33,  26,   3,
    -18,  -4,  21,  24,  27,  23,   9, -11,
    -19,  -3,  11,  21,  23,  16,   7,  -9,
    -27, -11,   4,  13,  14,   4,  -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43
]

mg_pesto_table = [
    mg_pawn_table,
    mg_knight_table,
    mg_bishop_table,
    mg_rook_table,
    mg_queen_table,
    mg_king_table
]

eg_pesto_table = [
    eg_pawn_table,
    eg_knight_table,
    eg_bishop_table,
    eg_rook_table,
    eg_queen_table,
    eg_king_table
]

gamephaseInc = [0,0,1,1,1,1,2,2,4,4,0,0]

mg_table = [
    [82, 82, 82, 82, 82, 82, 82, 82, 180, 216, 143, 177, 150, 208, 116, 71, 76, 89, 108, 113, 147, 138, 107, 62, 68, 95, 88, 103, 105, 94, 99, 59, 55, 80, 77, 94, 99, 88, 92, 57, 56, 78, 78, 72, 85, 85, 115, 70, 47, 81, 62, 59, 67, 106, 120, 60, 82, 82, 82, 82, 82, 82, 82, 82, ],
    [82, 82, 82, 82, 82, 82, 82, 82, 47, 81, 62, 59, 67, 106, 120, 60, 56, 78, 78, 72, 85, 85, 115, 70, 55, 80, 77, 94, 99, 88, 92, 57, 68, 95, 88, 103, 105, 94, 99, 59, 76, 89, 108, 113, 147, 138, 107, 62, 180, 216, 143, 177, 150, 208, 116, 71, 82, 82, 82, 82, 82, 82, 82, 82, ],
    [170, 248, 303, 288, 398, 240, 322, 230, 264, 296, 409, 373, 360, 399, 344, 320, 290, 397, 374, 402, 421, 466, 410, 381, 328, 354, 356, 390, 374, 406, 355, 359, 324, 341, 353, 350, 365, 356, 358, 329, 314, 328, 349, 347, 356, 354, 362, 321, 308, 284, 325, 334, 336, 355, 323, 318, 232, 316, 279, 304, 320, 309, 318, 314, ],
    [232, 316, 279, 304, 320, 309, 318, 314, 308, 284, 325, 334, 336, 355, 323, 318, 314, 328, 349, 347, 356, 354, 362, 321, 324, 341, 353, 350, 365, 356, 358, 329, 328, 354, 356, 390, 374, 406, 355, 359, 290, 397, 374, 402, 421, 466, 410, 381, 264, 296, 409, 373, 360, 399, 344, 320, 170, 248, 303, 288, 398, 240, 322, 230, ],
    [336, 369, 283, 328, 340, 323, 372, 357, 339, 381, 347, 352, 395, 424, 383, 318, 349, 402, 408, 405, 400, 415, 402, 363, 361, 370, 384, 415, 402, 402, 372, 363, 359, 378, 378, 391, 399, 377, 375, 369, 365, 380, 380, 380, 379, 392, 383, 375, 369, 380, 381, 365, 372, 386, 398, 366, 332, 362, 351, 344, 352, 353, 326, 344, ],
    [332, 362, 351, 344, 352, 353, 326, 344, 369, 380, 381, 365, 372, 386, 398, 366, 365, 380, 380, 380, 379, 392, 383, 375, 359, 378, 378, 391, 399, 377, 375, 369, 361, 370, 384, 415, 402, 402, 372, 363, 349, 402, 408, 405, 400, 415, 402, 363, 339, 381, 347, 352, 395, 424, 383, 318, 336, 369, 283, 328, 340, 323, 372, 357, ],
    [509, 519, 509, 528, 540, 486, 508, 520, 504, 509, 535, 539, 557, 544, 503, 521, 472, 496, 503, 513, 494, 522, 538, 493, 453, 466, 484, 503, 501, 512, 469, 457, 441, 451, 465, 476, 486, 470, 483, 454, 432, 452, 461, 460, 480, 477, 472, 444, 433, 461, 457, 468, 476, 488, 471, 406, 458, 464, 478, 494, 493, 484, 440, 451, ],
    [458, 464, 478, 494, 493, 484, 440, 451, 433, 461, 457, 468, 476, 488, 471, 406, 432, 452, 461, 460, 480, 477, 472, 444, 441, 451, 465, 476, 486, 470, 483, 454, 453, 466, 484, 503, 501, 512, 469, 457, 472, 496, 503, 513, 494, 522, 538, 493, 504, 509, 535, 539, 557, 544, 503, 521, 509, 519, 509, 528, 540, 486, 508, 520, ],
    [997, 1025, 1054, 1037, 1084, 1069, 1068, 1070, 1001, 986, 1020, 1026, 1009, 1082, 1053, 1079, 1012, 1008, 1032, 1033, 1054, 1081, 1072, 1082, 998, 998, 1009, 1009, 1024, 1042, 1023, 1026, 1016, 999, 1016, 1015, 1023, 1021, 1028, 1022, 1011, 1027, 1014, 1023, 1020, 1027, 1039, 1030, 990, 1017, 1036, 1027, 1033, 1040, 1022, 1026, 1024, 1007, 1016, 1035, 1010, 1000, 994, 975, ],
    [1024, 1007, 1016, 1035, 1010, 1000, 994, 975, 990, 1017, 1036, 1027, 1033, 1040, 1022, 1026, 1011, 1027, 1014, 1023, 1020, 1027, 1039, 1030, 1016, 999, 1016, 1015, 1023, 1021, 1028, 1022, 998, 998, 1009, 1009, 1024, 1042, 1023, 1026, 1012, 1008, 1032, 1033, 1054, 1081, 1072, 1082, 1001, 986, 1020, 1026, 1009, 1082, 1053, 1079, 997, 1025, 1054, 1037, 1084, 1069, 1068, 1070, ],
    [-65, 23, 16, -15, -56, -34, 2, 13, 29, -1, -20, -7, -8, -4, -38, -29, -9, 24, 2, -16, -20, 6, 22, -22, -17, -20, -12, -27, -30, -25, -14, -36, -49, -1, -27, -39, -46, -44, -33, -51, -14, -14, -22, -46, -44, -30, -15, -27, 1, 7, -8, -64, -43, -16, 9, 8, -15, 36, 12, -54, 8, -28, 24, 14, ],
    [-15, 36, 12, -54, 8, -28, 24, 14, 1, 7, -8, -64, -43, -16, 9, 8, -14, -14, -22, -46, -44, -30, -15, -27, -49, -1, -27, -39, -46, -44, -33, -51, -17, -20, -12, -27, -30, -25, -14, -36, -9, 24, 2, -16, -20, 6, 22, -22, 29, -1, -20, -7, -8, -4, -38, -29, -65, 23, 16, -15, -56, -34, 2, 13, ]
]

eg_table = [
    [94, 94, 94, 94, 94, 94, 94, 94, 272, 267, 252, 228, 241, 226, 259, 281, 188, 194, 179, 161, 150, 147, 176, 178, 126, 118, 107, 99, 92, 98, 111, 111, 107, 103, 91, 87, 87, 86, 97, 93, 98, 101, 88, 95, 94, 89, 93, 86, 107, 102, 102, 104, 107, 94, 96, 87, 94, 94, 94, 94, 94, 94, 94, 94, ],
    [94, 94, 94, 94, 94, 94, 94, 94, 107, 102, 102, 104, 107, 94, 96, 87, 98, 101, 88, 95, 94, 89, 93, 86, 107, 103, 91, 87, 87, 86, 97, 93, 126, 118, 107, 99, 92, 98, 111, 111, 188, 194, 179, 161, 150, 147, 176, 178, 272, 267, 252, 228, 241, 226, 259, 281, 94, 94, 94, 94, 94, 94, 94, 94, ],
    [223, 243, 268, 253, 250, 254, 218, 182, 256, 273, 256, 279, 272, 256, 257, 229, 257, 261, 291, 290, 280, 272, 262, 240, 264, 284, 303, 303, 303, 292, 289, 263, 263, 275, 297, 306, 297, 298, 285, 263, 258, 278, 280, 296, 291, 278, 261, 259, 239, 261, 271, 276, 279, 261, 258, 237, 252, 230, 258, 266, 259, 263, 231, 217, ],
    [252, 230, 258, 266, 259, 263, 231, 217, 239, 261, 271, 276, 279, 261, 258, 237, 258, 278, 280, 296, 291, 278, 261, 259, 263, 275, 297, 306, 297, 298, 285, 263, 264, 284, 303, 303, 303, 292, 289, 263, 257, 261, 291, 290, 280, 272, 262, 240, 256, 273, 256, 279, 272, 256, 257, 229, 223, 243, 268, 253, 250, 254, 218, 182, ],
    [283, 276, 286, 289, 290, 288, 280, 273, 289, 293, 304, 285, 294, 284, 293, 283, 299, 289, 297, 296, 295, 303, 297, 301, 294, 306, 309, 306, 311, 307, 300, 299, 291, 300, 310, 316, 304, 307, 294, 288, 285, 294, 305, 307, 310, 300, 290, 282, 283, 279, 290, 296, 301, 288, 282, 270, 274, 288, 274, 292, 288, 281, 292, 280, ],
    [274, 288, 274, 292, 288, 281, 292, 280, 283, 279, 290, 296, 301, 288, 282, 270, 285, 294, 305, 307, 310, 300, 290, 282, 291, 300, 310, 316, 304, 307, 294, 288, 294, 306, 309, 306, 311, 307, 300, 299, 299, 289, 297, 296, 295, 303, 297, 301, 289, 293, 304, 285, 294, 284, 293, 283, 283, 276, 286, 289, 290, 288, 280, 273, ],
    [525, 522, 530, 527, 524, 524, 520, 517, 523, 525, 525, 523, 509, 515, 520, 515, 519, 519, 519, 517, 516, 509, 507, 509, 516, 515, 525, 513, 514, 513, 511, 514, 515, 517, 520, 516, 507, 506, 504, 501, 508, 512, 507, 511, 505, 500, 504, 496, 506, 506, 512, 514, 503, 503, 501, 509, 503, 514, 515, 511, 507, 499, 516, 492, ],
    [503, 514, 515, 511, 507, 499, 516, 492, 506, 506, 512, 514, 503, 503, 501, 509, 508, 512, 507, 511, 505, 500, 504, 496, 515, 517, 520, 516, 507, 506, 504, 501, 516, 515, 525, 513, 514, 513, 511, 514, 519, 519, 519, 517, 516, 509, 507, 509, 523, 525, 525, 523, 509, 515, 520, 515, 525, 522, 530, 527, 524, 524, 520, 517, ],
    [927, 958, 958, 963, 963, 955, 946, 956, 919, 956, 968, 977, 994, 961, 966, 936, 916, 942, 945, 985, 983, 971, 955, 945, 939, 958, 960, 981, 993, 976, 993, 972, 918, 964, 955, 983, 967, 970, 975, 959, 920, 909, 951, 942, 945, 953, 946, 941, 914, 913, 906, 920, 920, 913, 900, 904, 903, 908, 914, 893, 931, 904, 916, 895, ],
    [903, 908, 914, 893, 931, 904, 916, 895, 914, 913, 906, 920, 920, 913, 900, 904, 920, 909, 951, 942, 945, 953, 946, 941, 918, 964, 955, 983, 967, 970, 975, 959, 939, 958, 960, 981, 993, 976, 993, 972, 916, 942, 945, 985, 983, 971, 955, 945, 919, 956, 968, 977, 994, 961, 966, 936, 927, 958, 958, 963, 963, 955, 946, 956, ],
    [-74, -35, -18, -18, -11, 15, 4, -17, -12, 17, 14, 17, 17, 38, 23, 11, 10, 17, 23, 15, 20, 45, 44, 13, -8, 22, 24, 27, 26, 33, 26, 3, -18, -4, 21, 24, 27, 23, 9, -11, -19, -3, 11, 21, 23, 16, 7, -9, -27, -11, 4, 13, 14, 4, -5, -17, -53, -34, -21, -11, -28, -14, -24, -43, ],
    [-53, -34, -21, -11, -28, -14, -24, -43, -27, -11, 4, 13, 14, 4, -5, -17, -19, -3, 11, 21, 23, 16, 7, -9, -18, -4, 21, 24, 27, 23, 9, -11, -8, 22, 24, 27, 26, 33, 26, 3, 10, 17, 23, 15, 20, 45, 44, 13, -12, 17, 14, 17, 17, 38, 23, 11, -74, -35, -18, -18, -11, 15, 4, -17, ]
]


def score(board: chess.Board) -> int:
    mg = [0, 0]
    eg = [0, 0]
    game_phase = 0

    if board.outcome() is not None:
        winner = board.outcome().winner
        if winner is not None:
            if winner == chess.WHITE:
                return 100_000
            else:
                return -100_000
    # evaluate each piece
    for sq in range(64):
        pc = board.piece_at(sq)
        if pc is not None:
            color = 0 if pc.color == chess.WHITE else 1
            piece_index = (pc.piece_type-1)*2 + color
            mg[color] += mg_table[piece_index][sq]
            eg[color] += eg_table[piece_index][sq]
            game_phase += gamephaseInc[piece_index]

    # tapered eval
    side2move = 0 if board.turn == chess.WHITE else 1
    mg_score = mg[side2move] - mg[OTHER(side2move)]
    eg_score = eg[side2move] - eg[OTHER(side2move)]
    mg_phase = game_phase
    if mg_phase > 24:
        # in case of early promotion
        mg_phase = 24
    eg_phase = 24 - mg_phase
    return (mg_score * mg_phase + eg_score * eg_phase) // 24

flip = [
    56, 57, 58, 59, 60, 61, 62, 63,
    48, 49, 50, 51, 52, 53, 54, 55,
    40, 41, 42, 43, 44, 45, 46, 47,
    32, 33, 34, 35, 36, 37, 38, 39,
    24, 25, 26, 27, 28, 29, 30, 31,
    16, 17, 18, 19, 20, 21, 22, 23,
    8, 9, 10, 11, 12, 13, 14, 15,
    0, 1, 2, 3, 4, 5, 6, 7
]


def _init_tables():
    global mg_table, eg_table

    for i in range(64):
        mg_table[WHITE_PAWN][i] = mg_pawn_table[i]
        mg_table[BLACK_PAWN][i] = mg_pawn_table[flip[i]]
        mg_table[WHITE_KNIGHT][i] = mg_knight_table[i]
        mg_table[BLACK_KNIGHT][i] = mg_knight_table[flip[i]]
        mg_table[WHITE_BISHOP][i] = mg_bishop_table[i]
        mg_table[BLACK_BISHOP][i] = mg_bishop_table[flip[i]]
        mg_table[WHITE_ROOK][i] = mg_rook_table[i]
        mg_table[BLACK_ROOK][i] = mg_rook_table[flip[i]]
        mg_table[WHITE_QUEEN][i] = mg_queen_table[i]
        mg_table[BLACK_QUEEN][i] = mg_queen_table[flip[i]]
        mg_table[WHITE_KING][i] = mg_king_table[i]
        mg_table[BLACK_KING][i] = mg_knight_table[flip[i]]

        eg_table[WHITE_PAWN][i] = eg_pawn_table[i]
        eg_table[BLACK_PAWN][i] = eg_pawn_table[flip[i]]
        eg_table[WHITE_KNIGHT][i] = eg_knight_table[i]
        eg_table[BLACK_KNIGHT][i] = eg_knight_table[flip[i]]
        eg_table[WHITE_BISHOP][i] = eg_bishop_table[i]
        eg_table[BLACK_BISHOP][i] = eg_bishop_table[flip[i]]
        eg_table[WHITE_ROOK][i] = eg_rook_table[i]
        eg_table[BLACK_ROOK][i] = eg_rook_table[flip[i]]
        eg_table[WHITE_QUEEN][i] = eg_queen_table[i]
        eg_table[BLACK_QUEEN][i] = eg_queen_table[flip[i]]
        eg_table[WHITE_KING][i] = eg_king_table[i]
        eg_table[BLACK_KING][i] = eg_knight_table[flip[i]]

    for piece in range(6):
        for field in range(64):
            mg_table[piece][field] += mg_value[piece]
            eg_table[piece][field] += eg_value[piece]

_init_tables()

class PestoStrategy(IStrategy):
    def __init__(self, rollout_depth: int = 4):
        super().__init__(rollout_depth)

    def pick_next_move(self, board: chess.Board) -> chess.Move | None:
        def score_move(move: chess.Move):
            bc = board.copy(stack=False)
            bc.push(move)
            return move, score(bc)

        moves = [score_move(move) for move in board.legal_moves]
        ##print(board.turn, [m[1] for m in moves])
        if board.turn != chess.WHITE:
            best_move = max(moves, key=lambda m: m[1])
        else:
            best_move = min(moves, key=lambda m: m[1])
        #print(best_move)
        return best_move[0]

    def analyze_board(self, board: chess.Board) -> int:
        return score(board)

#print("WHITE_PAWN", WHITE_PAWN)
#print("BLACK_PAWN", BLACK_PAWN)
#print("WHITE_KNIGHT", WHITE_KNIGHT)
#print("BLACK_KNIGHT", BLACK_KNIGHT)
#print("WHITE_BISHOP", WHITE_BISHOP)
#print("BLACK_BISHOP", BLACK_BISHOP)
#print("WHITE_ROOK", WHITE_ROOK)
#print("BLACK_ROOK", BLACK_ROOK)
#print("WHITE_QUEEN", WHITE_QUEEN)
#print("BLACK_QUEEN", BLACK_QUEEN)
#print("WHITE_KING", WHITE_KING)
#print("BLACK_KING", BLACK_KING)
#print("EMPTY", EMPTY)


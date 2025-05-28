"""
Constants used throughout the application
"""

# Age categories
AGE_CATEGORIES = {
    'AA': (21, 26), 'A': (27, 35), 'B': (36, 42), 'C': (43, 49),
    'D': (50, 54), 'E': (55, 59), 'F': (60, 64), 'G': (65, 69),
    'H': (70, 74), 'I': (75, 79), 'J': (80, 84), 'K': (85, 100)
}

# Event data from the provided schedule
EVENTS_DATA = {
    'Thursday': [
        (153, "PR2 Men's Masters 2x"), (154, "PR3 Women's Master Inclusive 2x"), (155, "PR2 Men's Masters 1x"),
        (156, "PR3 Men's Masters 1x"), (157, "Mixed B 4+"), (158, "Mixed D 2x"), (159, "Mixed F 2x"),
        (160, "Men's Open A 1x"), (161, "Women's Open AA 1x"), (162, "Men's Open C 4+"), (163, "Women's Open C 8+"),
        (164, "Men's Open E 1x"), (165, "Women's Open E 2x"), (166, "Men's Open G 2x"), (167, "Women's Ltwt D-E 4x"),
        (168, "Women's Ltwt F-K 4x"), (169, "Women's Club C 4x"), (170, "Mixed F 8+"), (171, "Mixed G-K 8+"),
        (172, "Women's Ltwt C 4+"), (173, "Men's Open AA 4+"), (174, "Men's Open B 2-"), (175, "Women's Ltwt B 1x"),
        (176, "Men's Open D 2-"), (177, "Women's Club D 8+"), (178, "Men's Ltwt F 2x"), (179, "Women's Open G-K 4+"),
        (180, "Men's Open H 2x"), (181, "Women's Open D-E 2-"), (182, "Women's Open F-K 2-"), (183, "Mixed E 4x"),
        (184, "Men's Ltwt A-C 4x"), (185, "Women's Open AA-B 4-"), (186, "Mixed D 8+"), (187, "Men's Club A 4+"),
        (188, "Women's Club A 4+"), (189, "Men's Open C 4x"), (190, "Women's Open C 4x"), (191, "Men's Open E 2-"),
        (192, "Women's Open F 4+"), (193, "Women's Ltwt E 1x"), (194, "Men's Open F-K 8+"), (195, "Women's Club B 4x"),
        (196, "Men's Ltwt D-K 4x"), (197, "Men's Open AA 4x"), (198, "Women's Open AA 4x"), (199, "Men's Open A 4x"),
        (200, "Women's Open A 4x"), (201, "Men's Ltwt B 1x"), (202, "Women's Open B 8+"), (203, "Men's Open D 1x"),
        (204, "Women's Open D 2x"), (205, "Men's Open F 1x"), (206, "Women's Open F 2x"), (207, "Men's Open I 1x"),
        (208, "Mixed A 4+"), (209, "Mixed C 4+"), (210, "Men's Club E 8+"), (211, "Men's Club F-K 8+"),
        (212, "Parent Child, M/S, F/D 2x")
    ],
    'Friday': [
        (217, "PR2 Mixed Masters 2x"), (218, "PR3 Women's Masters 1x"), (219, "PR3 Men's Masters Inclusive 2x"),
        (220, "Mixed E 4+"), (221, "Mixed C 2x"), (222, "Mixed A 2x"), (223, "Men's Open I 2x"),
        (224, "Men's Open J-K 2x"), (225, "Women's Open F 1x"), (226, "Men's Ltwt F 1x"), (227, "Women's Open D 8+"),
        (228, "Men's Ltwt D 1x"), (229, "Women's Open B 2x"), (230, "Men's Open B 4+"), (231, "Women's Ltwt A 4+"),
        (232, "Men's Ltwt A-C 4+"), (233, "Women's Ltwt E-K 4+"), (234, "Men's Club D 8+"), (235, "Men's Ltwt G 1x"),
        (236, "Women's Club E 4x"), (237, "Women's Club F 4x"), (238, "Women's Club G-K 4x"), (239, "Men's Open E 4x"),
        (240, "Women's Club C 4+"), (241, "Men's Club C 4+"), (242, "Women's Open AA 2x"), (243, "Men's Open A 8+"),
        (244, "Women's Club B 8+"), (245, "Men's Open B 4x"), (246, "Women's Open D-E 4-"), (247, "Women's Open F 4-"),
        (248, "Men's Club E 4+"), (249, "Women's Ltwt C 2x"), (250, "Men's Ltwt I-K 2x"), (251, "Men's Ltwt H 2x"),
        (252, "Women's Ltwt G-J 1x"), (253, "Women's Ltwt F 1x"), (254, "Men's Open F 2-"), (255, "Women's Ltwt D 1x"),
        (256, "Men's Ltwt D 2x"), (257, "Women's Ltwt B 2x"), (258, "Men's Ltwt B 2x"), (259, "Women's Open A 2-"),
        (260, "Women's Open AA 2-"), (261, "Men's Open AA - A 2x"), (262, "Women's Ltwt E 2x"), (263, "Mixed F-K 4+"),
        (264, "Women's Open G 1x"), (265, "Women's Open H-K 1x"), (266, "Men's Open G 4x"), (267, "Men's Open H 4x"),
        (268, "Men's Open I-K 4x"), (269, "Women's Open E 1x"), (270, "Men's Ltwt E 1x"), (271, "Women's Open C 4+"),
        (272, "Men's Open C 1x"), (273, "Women's Open A 2x"), (274, "Men's Open A 2x"), (275, "Men's Open E 4-"),
        (276, "Men's Open F 4-"), (277, "Men's Open D 4-"), (278, "Mixed B 8+"), (279, "Parent/Child F/S 2x")
    ],
    'Saturday': [
        (280, "PR2 Women's Masters 1x"), (281, "PR2 Men's Masters Inclusive 2x"), (282, "PR2 Mixed Masters 2x"),
        (283, "PR3 Mixed Masters 2x"), (284, "Mixed B 2x"), (285, "Mixed D 4x"), (286, "Mixed F 4x"),
        (287, "Men's Ltwt A1x"), (288, "Men's Ltwt AA 1x"), (289, "Women's Open A 4+"), (290, "Men's Open C 2x"),
        (291, "Women's Open C 1x"), (292, "Men's Open E 2x"), (293, "Women's Open E 8+"), (294, "Men's Open G 1x"),
        (295, "Women's Ltwt D 4+"), (296, "Men's Club G-K 4+"), (297, "Women's Ltwt A-C 4x"), (298, "Men's Open AA-A 4-"),
        (299, "Mixed A 8+"), (300, "Men's Open B 8+"), (301, "Women's Open B 4x"), (302, "Men's Open D 4+"),
        (303, "Women's Club D 4+"), (304, "Men's Open F 4+"), (305, "Women's Club E 8+"), (306, "Women's Club F-K 8+"),
        (307, "Men's Open H 1x"), (308, "Open Gender Open 2x"), (309, "Men's Open C 2-"), (310, "Men's Club A 8+"),
        (311, "Mixed G 4x"), (312, "Mixed H-I 4x"), (313, "Women's Ltwt B 4+"), (314, "Women's Ltwt D 2x"),
        (315, "Men's Open AA 1x"), (316, "Women's Ltwt AA-A 1x"), (317, "Men's Ltwt C 2x"), (318, "Women's Club C 8+"),
        (319, "Women's Open F 4x"), (320, "Men's Open E 8+"), (321, "Women's Club E 4+"), (322, "Men's Open H 2-"),
        (323, "Men's Open I-K 2-"), (324, "Men's Ltwt D-K 4+"), (325, "Women's Ltwt F 2x"), (326, "Women's Ltwt G 2x"),
        (327, "Women's Ltwt H-K 2x"), (328, "Women's Open C 2-"), (329, "Men's Club C 8+"), (330, "Men's Open B 2x"),
        (331, "Women's Open B 4+"), (332, "Men's Open D 2x"), (333, "Women's Open D 1x"), (334, "Men's Open F 4x"),
        (335, "Women's Open G 4x"), (336, "Women's Open H-K 4x"), (337, "Men's Open J-K 1x"), (338, "Women's Club A 8+"),
        (339, "Mixed Open C 4x"), (340, "Women's Open B 1x"), (341, "Mixed Open E 2x"), (342, "Parent/Child M/D 2x"),
        (343, "Men's Club B 8+")
    ],
    'Sunday': [
        (344, "PR1 Women's Masters 1x"), (345, "PR1 Men's Masters 1x"), (346, "PR2 Women's Masters Inclusive 2x"),
        (347, "PR3 Mixed Masters Inclusive 4+"), (348, "Mixed G 2x"), (349, "Mixed E 8+"), (350, "Mixed C 8+"),
        (351, "Women's Open AA 4+"), (352, "Men's Ltwt I-K 1x"), (353, "Women's Club F 4+"), (354, "Women's Club G-K 4+"),
        (355, "Men's Open F 2x"), (356, "Women's Open D 4+"), (357, "Men's Open D 8+"), (358, "Women's Club B 4+"),
        (359, "Men's Open B 1x"), (360, "Mixed A 4x"), (361, "Mixed H-K 2x"), (362, "Men's Club A 4x"),
        (363, "Men's Club B 4x"), (364, "Men's Club C 4x"), (365, "Men's Club D 4x"), (366, "Men's Ltwt G 2x"),
        (367, "Women's Open E 4x"), (368, "Men's Ltwt E 2x"), (369, "Women's Ltwt C 1x"), (370, "Men's Ltwt C 1x"),
        (371, "Women's Open A 8+"), (372, "Men's Open A 2-"), (373, "Men's Open AA 2-"), (374, "Open Gender Club 2x"),
        (375, "Women's Open B 2-"), (376, "Men's Ltwt A 2x"), (377, "Men's Open B-C 4-"), (378, "Men's Open G-K 4-"),
        (379, "Women's Open C 4-"), (380, "Men's Ltwt H 1x"), (381, "Women's Open F-K 8+"), (382, "Men's Club F 4+"),
        (383, "Women's Open D 4x"), (384, "Men's Open D 4x"), (385, "Men's Club B 4+"), (386, "Men's Club D 4+"),
        (387, "Women's Club A 4x"), (388, "Women's Ltwt A 2x"), (389, "Women's Club D 4x"), (390, "Men's Open G 4+"),
        (391, "Men's Open H - K 4+"), (392, "Women's Open E 4+"), (393, "Men's Open E 4+"), (394, "Women's Open C 2x"),
        (395, "Men's Open C 8+"), (396, "Women's Open A 1x"), (397, "Men's Open A 4+"), (398, "Men's Club E-F 4x"),
        (399, "Men's Club G-K 4x"), (400, "Mixed Open D 4+"), (401, "Mixed Open B 4x"), (402, "Women's Open G-K 2x"),
        (403, "Mixed Masters Open AA-K Ltwt 2x")
    ]
}
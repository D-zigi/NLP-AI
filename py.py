# def compareStrings(string1, string2):
#     n, m = len(string1), len(string2)
#     if n > m:
#         string1, string2 = string2, string1
#         n, m = m, n
        
#     i, j = 0, 0
#     string = [""] * n
#     while i < n and j < m:

#         if string1[i] == " ":
#             i += 1
#             continue
#         if string2[j] == " ":
#             j += 1
#             continue

#         if string1[i] != string2[j]:
#             string[i] += string2[j]
#             j += 1

#         else:
#             if len(string[i]) > 1:
#                 string[i] = f"'{string[i]}'"
#             else:
#                 string[i] = string1[i]
#             i += 1
        
#     # if len(string) == n:
#     #     string += [0] * (m - n)
#     return string

# str1 = "this is my style <style> body { color: red !important; } </style> for you"
# str2 = "this is my style  for you"

# string = compareStrings(str1, str2)
# print(string)
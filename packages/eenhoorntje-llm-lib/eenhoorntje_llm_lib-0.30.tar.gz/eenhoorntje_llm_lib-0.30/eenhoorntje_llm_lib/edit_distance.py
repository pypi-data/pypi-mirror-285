def get_shortest_edit_path(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i

    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1

    i, j = m, n
    operations = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
            i, j = i - 1, j - 1
        else:
            if i > 0 and dp[i][j] == dp[i - 1][j] + 1:
                operations.append(('remove', s1[i - 1], i - 1))
                i -= 1
            elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
                operations.append(('add', s2[j - 1], i - 1))
                j -= 1
            else:
                operations.append(('change', s1[i - 1], s2[j - 1], i - 1))
                i -= 1
                j -= 1

    return operations


def apply_edit_path(word, changes):
    for change in changes:
        if change[0] == "add":
            if change[2] < 0:
                return None
            if len(word) <= change[2]:
                return None
            word = word[:change[2] + 1] + change[1] + word[change[2] + 1:]
        elif change[0] == "remove":
            if change[2] < 0:
                return None
            if len(word) <= change[2]:
                return None
            if word[change[2]] != change[1]:
                return None
            word = word[:change[2]] + word[change[2] + 1:]
        elif change[0] == "change":
            if change[3] < 0:
                return None
            if len(word) <= change[3]:
                return None
            if word[change[3]] != change[1]:
                return None
            word = word[:change[3]] + change[2] + word[change[3] + 1:]
    return word


def get_edit_distance(hypothesis, reference):
    shortest_edit_path = get_shortest_edit_path(hypothesis, reference)
    distance = len(shortest_edit_path) / len(reference)
    return distance

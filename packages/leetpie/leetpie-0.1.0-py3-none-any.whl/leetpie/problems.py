from . import *


# 0019 ---- ---- ----
# [删除链表的倒数第 N 个结点](https://leetcode.cn/problems/remove-nth-node-from-end-of-list/description/)
# Medium
class S_19(Solution):

    testcase = {
        'id': 19,
        'input': [
            {'head': LinkedList([1, 2, 3, 4, 5]).head, 'n': 2},
            {'head': LinkedList([1]).head, 'n': 1},
        ],
        'output': [
            [1, 2, 3, 5],
            [],
        ]
    }

    def solve(self, head, n):
        hat = ListNode(next=head)
        backward = forward = hat
        for _ in range(n):
            forward = forward.next
        while forward.next:
            backward = backward.next
            forward = forward.next
        backward.next = backward.next.next
        # return hat.next
        return LinkedList.to_list(hat.next)
# ---- ---- ---- ----


# 0046 ---- ---- ----
# [全排列](https://leetcode.cn/problems/permutations/description/)
# Medium
class S_46(Solution):

    testcase = {
        'id': 46,
        'input': {'nums': [1, 2, 3]},
        'output': [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]],
    }

    def solve(self, nums):

        def inner():
            if len(tmp) == n:
                res.append(tmp.copy())

            for i in range(n):
                if permuted[i]:
                    continue
                tmp.append(nums[i])
                permuted[i] = True
                inner()
                tmp.pop()
                permuted[i] = False

        res = []
        tmp = []
        n = len(nums)
        permuted = [False] * n
        inner()
        return res
# ---- ---- ---- ----


# 0047 ---- ---- ----
# [全排列 II](https://leetcode.cn/problems/permutations-ii/description/)
# Medium
class S_47(Solution):

    testcase = {
        'id': 47,
        'input': {'nums': [1, 1, 2]},
        'output': [[1, 1, 2], [1, 2, 1], [2, 1, 1]]
    }

    def solve(self, nums):

        def inner():
            if len(tmp) == n:
                res.append(tmp.copy())

            for i in range(n):
                if permuted[i] or (i > 0 and not permuted[i-1] and nums[i] == nums[i-1]):
                    continue
                tmp.append(nums[i])
                permuted[i] = True
                inner()
                tmp.pop()
                permuted[i] = False

        res = []
        tmp = []
        n = len(nums)
        permuted = [False] * n
        nums.sort()
        inner()
        return res
# ---- ---- ---- ----


# 0077 ---- ---- ----
# [组合](https://leetcode.cn/problems/combinations/description/)
# Medium
class S_77(Solution):

    testcase = {
        'id': 77,
        'input': {'n': 4, 'k': 2},
        'output': [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]],
    }

    def solve(self, n, k):

        def inner(idx=1):
            if len(tmp) == k:
                res.append(tmp.copy())
                return

            for i in range(idx, n + 1):
                tmp.append(i)
                inner(i + 1)
                tmp.pop()

        res = []
        tmp = []
        inner()
        return res
# ---- ---- ---- ----


# 0078 ---- ---- ----
# [子集](https://leetcode.cn/problems/subsets/description/)
# Medium
class S_78(Solution):

    testcase = {
        'id': 78,
        'input': {'nums': [1, 2, 3]},
        'output': [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]],
    }

    def solve(self, nums):

        def inner(idx=0):
            res.append(tmp.copy())
            for i in range(idx, n):
                tmp.append(nums[i])
                inner(i + 1)
                tmp.pop()

        res = []
        tmp = []
        n = len(nums)
        inner()
        return res
# ---- ---- ---- ----


# 0090 ---- ---- ----
# [子集 II](https://leetcode.cn/problems/subsets-ii/description/)
# Medium
class S_90(Solution):

    testcase = {
        'id': 90,
        'input': {'nums': [1, 2, 2]},
        'output': [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]],
    }

    def solve(self, nums):

        def inner(idx=0):
            res.append(tmp.copy())
            for i in range(idx, n):
                if i > idx and nums[i] == nums[i-1]:
                    continue
                tmp.append(nums[i])
                inner(i + 1)
                tmp.pop()

        res = []
        tmp = []
        n = len(nums)
        nums.sort()
        inner()
        return res
# ---- ---- ---- ----


# 0101 ---- ---- ----
# [对称二叉树](https://leetcode.cn/problems/symmetric-tree/description/)
# Easy
class S_101(Solution):

    testcase = {
        'id': 101,
        'input': {'root': Tree.tree(
            [1, 2, 3, None, None, 4, None, None, 2, 4, None, None, 3, None, None]
        )},
        'output': True
    }

    def solve(self, root):

        def inner(lnode: TreeNode | None, rnode: TreeNode | None):
            if lnode is None and rnode is None:
                return True
            elif lnode is None or rnode is None:
                return False
            elif lnode.val != rnode.val:
                return False
            elif not inner(lnode.left, rnode.right):
                return False
            elif inner(lnode.right, rnode.left):
                return True
            else:
                return False

        return inner(root.left, root.right)
# ---- ---- ---- ----

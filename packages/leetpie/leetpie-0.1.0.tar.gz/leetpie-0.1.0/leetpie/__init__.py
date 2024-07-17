class Solution:

    def test(self):
        print('---- ---- ---- ----')
        in_ = self.testcase['input']
        out = self.testcase['output']
        if isinstance(in_, list):
            print('id:', self.testcase['id'])
            assert len(in_) == len(out)
            for i, v in enumerate(in_):
                res = self.solve(**v)
                print('Output:  ', res)
                print('Expected:', out[i])
        else:
            res = self.solve(**in_)
            print('id:', self.testcase['id'])
            print('Output:  ', res)
            print('Expected:', out)
        print('---- ---- ---- ----\n')


class ListNode:

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class LinkedList:

    def __init__(self, a: list):
        self.head = ListNode()
        self.from_list(a)
        if self.head.next:
            self.head = self.head.next

    def from_list(self, a: list):
        cur = self.head
        for i in a:
            cur.next = ListNode(i)
            cur = cur.next

    @staticmethod
    def to_list(head: ListNode):
        lst = []
        cur = head
        while cur:
            lst.append(cur.val)
            cur = cur.next
        return lst


class TreeNode:

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Tree:

    @staticmethod
    def tree(a: list) -> TreeNode:

        def build():
            if a[0] is not None:
                root = TreeNode(a.pop(0))
                root.left = build()
                root.right = build()
            else:
                root = a.pop(0)
            return root

        return build()

    @staticmethod
    def preorder(root: TreeNode):

        def inner(node: TreeNode):
            if node:
                res.append(node.val)
                inner(node.left)
                inner(node.right)

        res = []
        inner(root)
        return res

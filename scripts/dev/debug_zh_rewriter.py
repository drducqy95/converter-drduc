import os
import sys

# Ensure project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

from src.engine.zh_structure_rewriter import rewrite_chinese_structure

def test():
    test_cases = [
        # Cat 1
        ("穿黑色风衣的男子走了过来。", "男子 穿风衣 黑色走了过来。"),
        ("穿着白色寿衣的老太", "老太 穿着寿衣 白色"),
        ("惨白腐烂的双手", "双手 惨白腐烂"),
        ("白色的眼球", "眼球 白色"),
        ("跪在那里的黑衣男子", "男子 黑衣 跪在那里"),
        
        # Cat 2
        ("老太的身躯", "身躯 của 老太"),
        ("张陈心里很害怕", "张陈心里很害怕"), # should not match
        ("男子的脖子被咬断", "脖子 của 男子bị 咬断"),
        ("其他的坟头", "其他的坟头"), # should not match because of negative lookbehind
        
        # Cat 3
        ("他穿着一件黑色风衣", "他穿着一件风衣 黑色"),
        ("白色的粉末", "粉末白色"),
        
        # Cat 4 & 5
        ("你妈妈才把你给抓起来", "你妈妈才抓你起来"),
        ("被一下咬断了", "bị 一下咬断了"),
        
        # Cat 6 & 7
        ("一只手伸了出来", "một bàn 手伸 ra đây"),
        ("两座墓碑", "hai tấm 墓碑"),
        
        # Phase 3
        ("这两个死党", "两个死党这"),
        ("这死女人", "死女人这"),
        ("清脆的高跟鞋的声音", "声音 của 高跟鞋 清脆"),
        ("棱角分明的脸", "脸 棱角分明"),
        
        # Phase 4
        ("两座墓碑面前", "面前 hai tấm 墓碑"),
        ("在他不远处的一个坟头上", "在上 一个坟头 他不远处"),
        ("看了面前的两座墓碑后", "后 看了面前的hai tấm 墓碑"),
        ("金溪县育方中学初二3班教室", "教室 初二3班 育方中学 金溪县"),
        
        # Phase 5
        ("除了这两座墓碑还伴着", "ngoài hai tấm 墓碑这 ra 还 伴着"),
        ("向旁边挤了挤椅子", "挤了挤椅子 向 旁边"),
        ("在课桌下面摸找着", "摸找着 在课桌下面"),
        
        # Phase 6
        ("张妈妈的声音", "妈妈 张的声音"),
        ("王大叔今年40多岁", "大叔 王今年hơn 40 岁"),
        ("第二章：婴儿的哭声", "章 二：婴儿的哭声"),
        ("从客厅的电视机前传来", "传来 từ 客厅的电视机前"),
        ("6年的保安", "保安 6 年")
    ]
    
    passed = 0
    for src, expected in test_cases:
        res = rewrite_chinese_structure(src)
        if res == expected:
            print(f"✅ PASS: {src} -> {res}")
            passed += 1
        else:
            print(f"❌ FAIL: {src}")
            print(f"   Expected: {expected}")
            print(f"   Got:      {res}")
            
    print(f"\n{passed}/{len(test_cases)} tests passed.")

if __name__ == "__main__":
    test()

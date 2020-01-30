import re
from operator import *
from pyparsing import *
import functools
from fn.monad import Option

from DiseasePedia.utils import *


def and_not(expr: ParseExpression, neg: ParseExpression):
    return expr.copy().addCondition(lambda s, loc, tok: not neg.canParseNext(s, loc))


def any_but(but):
    return OneOrMore(and_not(Regex("."), but)).addParseAction(''.join)


def define_to(expr: ParseExpression, val):
    if not callable(val):
        val = lambda: val
    return expr.copy().addParseAction(val)


def map_to_id(exprs):
    return map_to(exprs, lambda i, _: i)


def map_to(exprs, func):
    return Or(list(map(extracted(lambda idx, sep: define_to(sep, functools.partial(func, idx))),
                       enumerate(exprs))))


def _make_separator(indent_literals):
    return [
        Combine("(" + indent_literals + ")"),
        Combine(indent_literals + "." + ~Word(nums)),
        Combine("（" + indent_literals + "）"),
        Combine(indent_literals + "、")
    ]


class IndentComponents:
    def __init__(self, content=None):
        self.content = content
        self.children = []

    @classmethod
    def need_component(cls, c):
        return c if isinstance(c, cls) else cls(c)

    def add_component(self, c):
        self.children.append(self.need_component(c))

    def to_string(self, indent=2):
        if self.content is None:
            return '\n'.join(map(methodcaller('to_string', indent), self.children))
        return str(self.content) + '\n'.join(
            map(lambda s: indent * " " + s, map(methodcaller("to_string", indent), self.children)))

    def __str__(self):
        return self.to_string()


class ParagraphSplit:
    chn_nums = Word("一二三四五六七八九十")
    indent_digits = Word(nums)
    cirno_nums = Word("①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳⓪")
    indent_literal_list = [chn_nums, indent_digits, cirno_nums]
    indent_literals = Or(indent_literal_list)
    indent_literals_with_id = map_to_id(indent_literal_list)
    sentence_end = Word('。；', exact=1)
    comma_separate = ~sentence_end + any_but(sentence_end | Literal("：")) + Literal('：')
    distinct_separators = _make_separator(indent_literals)
    id_of_separator = map_to(_make_separator(indent_literals_with_id), lambda x, _, __, y: "{}{}".format(y[0], x))
    separators = Or(distinct_separators + [comma_separate])('Separators')
    content = any_but(separators) + FollowedBy(separators)
    items = ZeroOrMore(content).setResultsName('preleading') + OneOrMore(
        separators + content.setResultsName("content")).setResultsName('indented')

    @classmethod
    def _find_next(cls, part):
        print(part[0][0])
        indent = cls.id_of_separator.parseString(part[0][0])[0]
        for i, (idx, content) in enumerate(part[1:], 1):
            if cls.id_of_separator.parseString(idx)[0] == indent:
                return i
        return len(part)

    @classmethod
    def _make_indent(cls, part, prev, cur_indent, indent):
        skips = 0
        comp = IndentComponents()
        for idx, content in part:
            if skips:
                skips -= 1
                continue
            cur_idx = cls.id_of_separator.parseString(idx)[0]
            if cur_idx == prev or prev is None:
                prev = cur_idx
                comp.add_component(idx + content)
                # yield cur_indent * " " + idx + content
            else:
                skips = cls._find_next(part)
                print(part[1:skips])
                comp.add_component(cls._make_indent(part[1:skips], cur_idx, cur_indent + indent, indent))
        return comp

    @classmethod
    def make_indent(cls, part, indent=2):
        return '\n'.join(map(extracted(add), part))
        # return cls._make_indent(part, None, 0, indent).to_string(indent)

    @classmethod
    def indent_parts(cls, s):
        res = cls.items.parseString(s)
        ps = res.indented.asList()
        preleading = res.preleading[0] if res.preleading else ''
        return preleading + ('\n' if preleading else '') + cls.make_indent(
            [(idx, content) for idx, content in zip(ps[::2], ps[1::2])])

    @classmethod
    def try_indent(cls, s):
        return Option.from_call(cls.indent_parts, s).get_or(s)


if __name__ == '__main__':
    # s = '''1.治疗原则（1）恢复窦性心律 只有恢复窦性心律（正常心律），才能达到完全治疗房颤的目的，所以对于任何房颤病人均应该尝试恢复窦性心律的治疗方法。（2）控制快速心室率 对于不能恢复窦性心律的房颤病人，可以应用药物减慢较快的心室率。（3）防止血栓形成和脑卒中 房颤时如果不能恢复窦性心律，可以应用抗凝药物预防血栓形成和脑卒中的发生。对于某些疾病如甲亢、急性酒精中毒、药物所致的房颤，在祛除病因之后，房颤可能自行消失。2.药物治疗目前药物治疗依然是治疗房颤的重要方法，药物能恢复和维持窦性心律，控制心室率以及预防血栓栓塞并发症。转复窦性心律（正常节律）药物：对于新发房颤因其在48小时内的自行复窦的比例很高（24小时内约60%），可先观察，也可采用普罗帕酮或氟卡胺顿服的方法。房颤已经持续大于48小时而小于7天者，能用静脉药物转律的有氟卡胺、多非利特、普罗帕酮、伊布利特和胺碘酮等，成功率可达50%。房颤发作持续时间超过一周（持续性房颤）药物转律的效果大大降低，常用和证实有效的药物有胺碘酮、伊布利特、多非利特等。控制心室率（频率控制）的药物：控制心室率可以保证心脏基本功能，尽可能降低房颤引起的心脏功能紊乱。常用药物包括：（1）β受体阻滞剂 最有效、最常用和常常单独应用的药物；（2）钙通道拮抗剂 如维拉帕米和地尔硫卓也可有效用于房颤时的心室率控制，尤其对于运动状态下的心室率的控制优于地高辛，和地高辛合用的效果也优于单独使用。尤其多用于无器质性心脏病或左室收缩功能正常以及伴有慢性阻塞性肺疾病的患者；（3）洋地黄 在紧急情况下控制房颤心室率的一线用药，目前临床上多用于伴有左心衰时的心室率控制；（4）胺碘酮 可降低房颤时的心室率，不建议用于慢性房颤时的长期心室率控制，只是在其他药物控制无效或禁忌时、在房颤合并心力衰竭需紧急控制心室率时可首选胺碘酮与洋地黄合用。（5）抗凝治疗 是预防房颤病人血栓形成和栓塞的必要手段，房颤病人如果有下列情况，应当进行抗凝治疗：年龄≥65岁；以前有过脑卒中病史或者短暂脑缺血发作；充血性心力衰竭；高血压；糖尿病；冠心病；左心房扩大；超声心动图发现左心房血栓。抗凝治疗一定要有专科医生指导，抗凝过度可能导致出血，抗凝强度不够则没有预防作用。3.非药物治疗房颤的非药物治疗包括电转复（转复窦性心律）、射频消融治疗和外科迷宫手术治疗（彻底根治房颤）。（1）电复律 是指用两个电极片放置在病人胸部的适当部位，通过除颤仪发放电流，重新恢复窦性心律的方法。电复律适用于：紧急情况的房颤（如心肌梗死、心率极快、低血压、心绞痛、心衰等），房颤症状严重，病人难以耐受，上次电复律成功，未用药物维持而又复发的房颤。电复律不是根治房颤的方法，病人的房颤往往会复发，而且部分病人还需要继续服用抗心律失常药物维持窦性心律。（2）导管消融治疗 适用于绝大多数房颤患者，创伤小，病人易于接受。（3）外科迷宫手术 目前主要用于因其他心脏疾病需要行心脏手术治疗的房颤病人，手术效果好，但是创伤大。'''
    s = "先天因素（35%）：心脏胚胎发育的关键时期是在妊娠的第2～8周，先天性心血管畸形也主要发生于此阶段，先天性心脏病的发生有多方面的原因，大致分为内在的和外部的两类，其中以后者多见，内在因素主要与遗传有关，特别是染色体易位和畸变，例如21-三体综合征，13-三体综合征，14-三体综合征，15-三体综合征和18-三体综合征等，常合并先天性心血管畸形。感染因素（45%）：此外，先天性心脏病患者子女的心血管畸形的发生率比预计发病率明显的多，外部因素中较重要的有宫内感染，尤其是病毒感染，如风疹，腮腺炎，流行性感冒及柯萨奇病毒等;其他如妊娠期接触大剂量射线。其他因素（10%）：使用某些药物，患代谢性疾病或慢性病，缺氧，母亲高龄(接近更年期)等，均有造成先天性心脏病的危险。发病机制1.病理解剖(1)室间隔缺损和肺动脉狭窄：是法洛四联症的主要病理解剖改变，因圆锥室间隔向前向左移位，与正常位置的窦部室间隔不能连接，故在主动脉口之下形成较大的室间隔缺损，可分为主动脉异常粗大右移：骑跨于室间隔之上，可同时接受左右心室的血流，主动脉骑跨与室间隔缺损的位置有关，但不论主动脉右移程度如何显著，主动脉瓣与二尖瓣前叶仍有解剖连续。"
    print(ParagraphSplit.indent_parts(s))

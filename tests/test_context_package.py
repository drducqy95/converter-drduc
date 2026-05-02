from src.context.entity_salience import EntitySalienceMemory
from src.context.mention_memory import MentionMemory
from src.context.register_policy import RegisterPolicy
from src.context.speaker_tracker import SpeakerTracker
from src.context.vi_pronoun_selector import VietnamesePronounSelector
from src.context.zero_pronoun_detector import ZeroPronounDetector
from src.eapee.pronoun_resolver import PronounResolver


def test_speaker_tracker_explicit_pair():
    tracker = SpeakerTracker()

    speaker, listener = tracker.update_from_sentence("林动对萧炎说道：“你来。”", ["林动", "萧炎"], is_dialogue=True)

    assert speaker == "林动"
    assert listener == "萧炎"


def test_speaker_tracker_implicit_alternation():
    tracker = SpeakerTracker()
    tracker.update_from_sentence("林动对萧炎说道：“你来。”", ["林动", "萧炎"], is_dialogue=True)

    speaker, listener = tracker.update_from_sentence("“好。”", ["林动", "萧炎"], is_dialogue=True)

    assert speaker == "萧炎"
    assert listener == "林动"


def test_speaker_tracker_extended_speech_verb():
    tracker = SpeakerTracker()

    speaker, _listener = tracker.update_from_sentence("韩立沉声道：“退下。”", ["韩立"], is_dialogue=True)

    assert speaker == "韩立"


def test_entity_salience_update_and_decay():
    memory = EntitySalienceMemory()
    memory.update("韓立", "subject", "s1", gender="male")
    before = memory.get_most_salient().salience_score

    memory.decay("s2")

    assert memory.get_most_salient().salience_score < before


def test_entity_salience_prefers_subject():
    memory = EntitySalienceMemory()
    memory.update("南宮婉", "object", "s1", gender="female")
    memory.update("韓立", "subject", "s1", gender="male")

    assert memory.get_most_salient().entity_id == "韓立"


def test_entity_salience_gender_filter():
    memory = EntitySalienceMemory()
    memory.update("南宮婉", "subject", "s1", gender="female")

    assert memory.get_most_salient(gender="female").entity_id == "南宮婉"


def test_zero_pronoun_detector_emits_candidate():
    memory = EntitySalienceMemory()
    memory.update("韓立", "subject", "s1")
    detector = ZeroPronounDetector()

    candidates = detector.detect("走進山谷。", memory, segment_id="s2")

    assert candidates
    assert candidates[0].entity_id == "韓立"


def test_zero_pronoun_detector_skips_dialogue():
    memory = EntitySalienceMemory()
    memory.update("韓立", "subject", "s1")
    detector = ZeroPronounDetector()

    assert detector.detect("走進山谷。", memory, is_dialogue=True) == []


def test_register_policy_selects_modern_gendered_pronoun():
    policy = RegisterPolicy()

    assert policy.select(register="modern", gender="female", role="subject") == "cô ấy"


def test_vi_pronoun_selector_uses_policy():
    selector = VietnamesePronounSelector()

    assert selector.select_pronoun(register="xianxia", gender="male") == "hắn"


def test_mention_memory_deduplicates_and_bounds():
    memory = MentionMemory(limit=3)

    memory.remember(["A", "B", "C", "A", "D"])

    assert memory.items == ["B", "C", "A", "D"][-3:]


def test_pronoun_resolver_uses_extracted_speaker_tracker():
    resolver = PronounResolver()

    context = resolver.detect_dialogue_context("林动对萧炎说道：“你来。”", ["林动", "萧炎"], context_type="dialogue")

    assert context["speaker"] == "林动"
    assert context["listener"] == "萧炎"

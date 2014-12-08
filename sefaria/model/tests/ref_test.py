# -*- coding: utf-8 -*-
import pytest
from sefaria.model import *
from sefaria.system.exceptions import InputError

class Test_Ref(object):

    def test_short_names(self):
        ref = Ref(u"Exo. 3:1")
        assert ref.book == u"Exodus"

    def test_normal_form_is_identifcal(self):
        assert Ref("Genesis 2:5").normal() == "Genesis 2:5"
        assert Ref("Shabbat 32b").normal() == "Shabbat 32b"
        assert Ref("Mishnah Peah 4:2-4").normal() == "Mishnah Peah 4:2-4"

    def test_bible_range(self):
        ref = Ref(u"Job.2:3-3:1")
        assert ref.toSections == [3, 1]

    def test_short_bible_refs(self):  # this behavior is changed from earlier
        assert Ref(u"Exodus") != Ref(u"Exodus 1")
        assert Ref(u"Exodus").padded_ref() == Ref(u"Exodus 1")

    def test_short_talmud_refs(self):  # this behavior is changed from earlier
        assert Ref(u"Sanhedrin 2a") != Ref(u"Sanhedrin")
        assert Ref(u"Sanhedrin 2a") == Ref(u"Sanhedrin 2")

    def test_each_title(object):
        for lang in ["en", "he"]:
            for t in library.full_title_list(lang, False):
                assert library.all_titles_regex(lang).match(t), u"'{}' doesn't resolve".format(t)

    def test_map(self):
        assert Ref("Me'or Einayim 16") == Ref("Me'or Einayim, Yitro")

    def test_comma(self):
        assert Ref("Me'or Einayim 24") == Ref("Me'or Einayim, 24")
        assert Ref("Genesis 18:24") == Ref("Genesis, 18:24")

    def test_padded_ref(self):
        assert Ref("Exodus").padded_ref().normal() == "Exodus 1"
        assert Ref("Exodus 1").padded_ref().normal() == "Exodus 1"
        assert Ref("Exodus 1:1").padded_ref().normal() == "Exodus 1:1"
        assert Ref("Rashi on Genesis 2:3:1").padded_ref().normal() == "Rashi on Genesis 2:3:1"

    def test_context_ref(self):
        assert Ref("Genesis 2:3").context_ref().normal() == "Genesis 2"
        assert Ref("Rashi on Genesis 2:3:1").context_ref().normal() == "Rashi on Genesis 2:3"
        assert Ref("Rashi on Genesis 2:3:1").context_ref(2).normal() == "Rashi on Genesis 2"

    def test_section_ref(self):
        assert Ref("Rashi on Genesis 2:3:1").section_ref().normal() == "Rashi on Genesis 2:3"
        assert Ref("Genesis 2:3").section_ref().normal() == "Genesis 2"
        assert Ref("Shabbat 4a").section_ref().normal() == "Shabbat 4a"

    def test_top_section_ref(self):
        assert Ref("Job 4:5").top_section_ref().normal() == "Job 4"
        assert Ref("Rashi on Genesis 1:2:3").top_section_ref().normal() == "Rashi on Genesis 1"
        assert Ref("Genesis").top_section_ref().normal() == "Genesis 1"

    def test_next_ref(self):
        assert Ref("Job 4:5").next_section_ref().normal() == "Job 5"
        assert Ref("Shabbat 4b").next_section_ref().normal() == "Shabbat 5a"
        assert Ref("Shabbat 5a").next_section_ref().normal() == "Shabbat 5b"
        assert Ref("Rashi on Genesis 5:32:2").next_section_ref().normal() == "Rashi on Genesis 6:2"
        assert Ref("Mekhilta 35.3").next_section_ref() is None
        # This will start to fail when we fill in this text
        assert Ref("Mekhilta 23:19").next_section_ref().normal() == "Mekhilta 31:12"

    def test_prev_ref(self):
        assert Ref("Job 4:5").prev_section_ref().normal() == "Job 3"
        assert Ref("Shabbat 4b").prev_section_ref().normal() == "Shabbat 4a"
        assert Ref("Shabbat 5a").prev_section_ref().normal() == "Shabbat 4b"
        assert Ref("Rashi on Genesis 6:2:1").prev_section_ref().normal() == "Rashi on Genesis 5:32"
        assert Ref("Mekhilta 12:1").prev_section_ref() is None
        # This will start to fail when we fill in this text
        assert Ref("Mekhilta 31:12").prev_section_ref().normal() == "Mekhilta 23:19"

    def test_range_depth(self):
        assert Ref("Leviticus 15:3 - 17:12").range_depth() == 2
        assert Ref("Leviticus 15-17").range_depth() == 2
        assert Ref("Leviticus 15:17-21").range_depth() == 1
        assert Ref("Leviticus 15:17").range_depth() == 0
        assert Ref("Shabbat 15a-16b").range_depth() == 2
        assert Ref("Shabbat 15a").range_depth() == 0
        assert Ref("Shabbat 15a:15-15b:13").range_depth() == 2

        assert Ref("Rashi on Leviticus 15:3-17:12").range_depth() == 3
        assert Ref("Rashi on Leviticus 15-17").range_depth() == 3
        assert Ref("Rashi on Leviticus 15:17-21").range_depth() == 2
        assert Ref("Rashi on Leviticus 15:17").range_depth() == 0
        assert Ref("Rashi on Shabbat 15a-16b").range_depth() == 3
        assert Ref("Rashi on Shabbat 15a").range_depth() == 0
        assert Ref("Rashi on Shabbat 15a:15-15b:13").range_depth() == 3
        assert Ref("Rashi on Exodus 3:1-4:1").range_depth() == 3
        assert Ref("Rashi on Exodus 3:1-4:10").range_depth() == 3
        assert Ref("Rashi on Exodus 3:1-3:10").range_depth() == 2
        assert Ref("Rashi on Exodus 3:1:1-3:1:3").range_depth() == 1


    def test_span_size(self):
        assert Ref("Leviticus 15:3 - 17:12").span_size() == 3
        assert Ref("Leviticus 15-17").span_size() == 3
        assert Ref("Leviticus 15:17-21").span_size() == 1
        assert Ref("Leviticus 15:17").span_size() == 1
        assert Ref("Shabbat 15a-16b").span_size() == 4
        assert Ref("Shabbat 15a").span_size() == 1
        assert Ref("Shabbat 15a:15-15b:13").span_size() == 2

        assert Ref("Rashi on Leviticus 15:3-17:12").span_size() == 3
        assert Ref("Rashi on Leviticus 15-17").span_size() == 3
        assert Ref("Rashi on Leviticus 15:17-21").span_size() == 5
        assert Ref("Rashi on Leviticus 15:17").span_size() == 1
        assert Ref("Rashi on Shabbat 15a-16b").span_size() == 4
        assert Ref("Rashi on Shabbat 15a").span_size() == 1
        assert Ref("Rashi on Shabbat 15a:15-15b:13").span_size() == 2
        assert Ref("Rashi on Exodus 3:1-4:1").span_size() == 2
        assert Ref("Rashi on Exodus 3:1-4:10").span_size() == 2

    def test_split_spanning_ref(self):
        assert Ref("Leviticus 15:3 - 17:12").split_spanning_ref() == [Ref('Leviticus 15:3-33'), Ref('Leviticus 16:1-34'), Ref('Leviticus 17:1-12')]
        assert Ref("Leviticus 15-17").split_spanning_ref() == [Ref('Leviticus 15:1-33'), Ref('Leviticus 16:1-34'), Ref('Leviticus 17:1-16')]
        assert Ref("Leviticus 15:17-21").split_spanning_ref() == [Ref('Leviticus 15:17-21')]
        assert Ref("Leviticus 15:17").split_spanning_ref() == [Ref('Leviticus 15:17')]
        assert Ref("Shabbat 15a-16b").split_spanning_ref() == [Ref('Shabbat 15a:1-55'), Ref('Shabbat 15b:1-36'), Ref('Shabbat 16a:1-15'), Ref('Shabbat 16b:1-43')]
        assert Ref("Shabbat 15a").split_spanning_ref() == [Ref('Shabbat 15a')]
        assert Ref("Shabbat 15a:15-15b:13").split_spanning_ref() == [Ref('Shabbat 15a:15-55'), Ref('Shabbat 15b:1-13')]
        assert Ref("Rashi on Exodus 5:3-6:7").split_spanning_ref() == [Ref('Rashi on Exodus 5:3:1'), Ref('Rashi on Exodus 5:4:1-2'), Ref('Rashi on Exodus 5:5:1'), Ref('Rashi on Exodus 5:6:1'), Ref('Rashi on Exodus 5:7:1-4'), Ref('Rashi on Exodus 5:8:1-4'), Ref('Rashi on Exodus 5:9:1'), Ref('Rashi on Exodus 5:11:1-2'), Ref('Rashi on Exodus 5:12:1'), Ref('Rashi on Exodus 5:13:1-2'), Ref('Rashi on Exodus 5:14:1-3'), Ref('Rashi on Exodus 5:16:1-2'), Ref('Rashi on Exodus 5:18:1'), Ref('Rashi on Exodus 5:19:1-2'), Ref('Rashi on Exodus 5:20:1'), Ref('Rashi on Exodus 5:22:1'), Ref('Rashi on Exodus 5:23:1')]

    def test_range_refs(self):
        assert Ref("Leviticus 15:12-17").range_list() ==  [Ref('Leviticus 15:12'), Ref('Leviticus 15:13'), Ref('Leviticus 15:14'), Ref('Leviticus 15:15'), Ref('Leviticus 15:16'), Ref('Leviticus 15:17')]
        assert Ref("Shabbat 15b:5-8").range_list() ==  [Ref('Shabbat 15b:5'), Ref('Shabbat 15b:6'), Ref('Shabbat 15b:7'), Ref('Shabbat 15b:8')]

        with pytest.raises(InputError):
            Ref("Shabbat 15a:13-15b:2").range_list()
        with pytest.raises(InputError):
            Ref("Exodus 15:12-16:1").range_list()

    def test_ref_regex(self):
        assert Ref("Exodus 15").regex() == u'^Exodus( 15$| 15:| 15 \\d)'
        assert Ref("Exodus 15:15-17").regex() == u'^Exodus( 15:15$| 15:15:| 15:15 \\d| 15:16$| 15:16:| 15:16 \\d| 15:17$| 15:17:| 15:17 \\d)'
        assert Ref("Yoma 14a").regex() == u'^Yoma( 14a$| 14a:| 14a \\d)'
        assert Ref("Yoma 14a:12-15").regex() == u'^Yoma( 14a:12$| 14a:12:| 14a:12 \\d| 14a:13$| 14a:13:| 14a:13 \\d| 14a:14$| 14a:14:| 14a:14 \\d| 14a:15$| 14a:15:| 14a:15 \\d)'
        assert Ref("Yoma").regex() == u'^Yoma($|:| \\d)'  # This is as legacy had it


class Test_Cache(object):
    def test_cache_identity(self):
        assert Ref("Ramban on Genesis 1") is Ref("Ramban on Genesis 1")
        assert Ref(u"שבת ד' כב.") is Ref(u"שבת ד' כב.")

    def test_obj_created_cache_identity(self):
        assert Ref("Job 4") is Ref("Job 4:5").top_section_ref()
        assert Ref("Rashi on Genesis 2:3:1").context_ref() is Ref("Rashi on Genesis 2:3")

    def test_different_tref_cache_identity(self):
        assert Ref("Genesis 27:3") is Ref("Gen. 27:3")
        assert Ref("Gen. 27:3") is Ref(u"בראשית כז.ג")

    def test_cache_clearing(self):
        r1 = Ref("Ramban on Genesis 1")
        Ref.clear_cache()
        r2 = Ref("Ramban on Genesis 1")
        assert r1 is not r2


class Test_normal_forms(object):
    def test_normal(self):
        assert Ref("Genesis 2:5").normal() == "Genesis 2:5"
        assert Ref("Shabbat 32b").normal() == "Shabbat 32b"
        assert Ref("Mishnah Peah 4:2-4").normal() == "Mishnah Peah 4:2-4"


    def test_url_form(self):
        assert Ref("Genesis 2:5").url() == "Genesis.2.5"
        assert Ref("Genesis 2:5-10").url() == "Genesis.2.5-10"
        assert Ref("Rashi on Shabbat 12a.10").url() == "Rashi_on_Shabbat.12a.10"



class Test_set_construction_from_ref(object):
    def test_ref_noteset(self):
        pass

    def test_ref_linkset(self):
        pass

'''
class Test_ref_manipulations():

    def test_section_level_ref(self):
        assert t.section_level_ref("Rashi on Genesis 2:3:1") == "Rashi on Genesis 2:3"
        assert t.section_level_ref("Genesis 2:3") == "Genesis 2"
        assert t.section_level_ref("Shabbat 4a") == "Shabbat 4a"

    def test_list_refs_in_range(self):
        assert t.list_refs_in_range("Job 4:5-9") == ["Job 4:5","Job 4:6","Job 4:7","Job 4:8","Job 4:9"]
        assert t.list_refs_in_range("Genesis 2:3") == ["Genesis 2:3"]
'''
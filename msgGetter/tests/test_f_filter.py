# ABOUTME: Tests for filtering the markdown of a thread into the text to embed
# ABOUTME: Covers the button text Google Groups shows beside a post

from f_filter import filter_markdown

OWN_POST = ("[Original Message ID:FRHklv4VJU0](https://groups.google.com/g/cozy_builders/c/x)\n"
            "# CozyRAG\n\n### tklenke\n\n"
            "<author@example.com> Nov 2, 2026, 2:08:54 PM Nov 2 Reply to authorYou cannot reply "
            "privately to your own messageForward Delete Copy link Report messageYou cannot "
            "report your own messageShow original message to COZY Builders Mailing List"
            "A couple responses you might want to look at")

OTHER_POST = ("[Original Message ID:IO1b3H0WdYI](https://groups.google.com/g/cozy_builders/c/x)\n"
              "# Nose gear\n\n### Mike\n\n"
              "<author@example.com> Sep 29, 2025, 8:22:26 AM 9/29/25 Reply to author Forward "
              "DeleteYou do not have permission to delete messages in this groupCopy link "
              "Report messageShow original message to COZY Builders Mailing List"
              "The nose gear shimmies")


def get_words(strMarkdown):
    return " ".join(filter_markdown(strMarkdown).split())


def test_button_text_of_an_own_post_is_removed():
    strText = get_words(OWN_POST)
    for strButton in ("cannot", "Reply to author", "Forward", "Copy link", "Report message",
                      "Show"):
        assert strButton.lower() not in strText.lower()


def test_text_of_an_own_post_is_kept():
    assert "A couple responses you might want to look at" in get_words(OWN_POST)


def test_post_of_another_author_is_filtered_the_same():
    strText = get_words(OTHER_POST)
    assert "The nose gear shimmies" in strText
    assert "permission" not in strText


def test_own_words_about_replying_are_kept():
    strPost = OWN_POST.replace("A couple responses", "You cannot reply to a couple responses")
    assert "You cannot reply to a couple responses" in get_words(strPost)

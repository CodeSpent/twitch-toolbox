from PyInquirer import style_from_dict, Token, prompt, Separator


twitch_theme = style_from_dict(
    {
        Token.QuestionMark: "#E91E63 bold",
        Token.Selected: "#673AB7 bold",
        Token.Answer: "#2196f3 bold",
    }
)

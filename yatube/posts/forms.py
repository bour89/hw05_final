from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):

    def clean_text(self):
        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError('Пустой текст записи')
        return text

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст поста',
                  'group': 'Группа поста'}
        help_text = {'text': 'Текст нового поста',
                     'group': 'Группа, к которой относится пост'}


class CommentForm(forms.ModelForm):

    def clean_text(self):
        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError('Пустой текст комментария')
        return text

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Комментария'}
        help_text = {'text': 'Текст комментария'}

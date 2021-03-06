from django.shortcuts import render ,get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger
from .forms import EmailPostForm
from django.core.mail import send_mail
from .models import Comment
from .forms import CommentForm
from taggit.models import Tag

# Create your views here.
def post_list(request,tag_slug=None):
    posts_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts_list.filter(tags__in[tag])
    paginator = Paginator(posts_list, 3) #3 post in each Page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
    #    if page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is out of range, deliver last page of result
        posts = paginator.page(paginator.num_pages)

    return render(request,'blog/post/list.html',{'page':page, 'posts':posts,'tag':tag})
def post_detail(request,year,month,day,post):
    #list of post with given criteria
    post = get_object_or_404(Post, slug=post,status='published',publish__year=year,
    publish__month=month,publish__day=day)
    #list of active post for above comment
    comments = post.comments.filter(active=True)
    if request.method == 'POST':
        #a comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            #create comment object but dont dave to database yet
            new_comment = comment_form.save(commit=False)
            new_comment.post = post

            #save comment to DB
            new_comment.save()
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post':post, 'comment_form':comment_form,'comments':comments})


def post_share(request,post_id):
    #retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        #form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            #send Email
            post_url = request.build_absolute_uri(post.get_absolute_url)
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title,post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'ablesbizzy@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post':post, 'form':form, 'sent':sent})

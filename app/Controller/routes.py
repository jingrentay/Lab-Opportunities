from __future__ import print_function
import sys
import random
from flask import Blueprint
from flask import render_template, flash, redirect, url_for, request
from config import Config

from app import db, num_collector
from app.Model.models import Application, Field, Post, Major, User, Student, Faculty, postMajors
from app.Controller.forms import ApplicationForm, PostForm, ProfileForm, SortForm
from flask_login import current_user, login_user, logout_user, login_required



bp_routes = Blueprint('routes', __name__)
bp_routes.template_folder = Config.TEMPLATE_FOLDER #'..\\View\\templates'

# ================================================================
#   Name:           rand_quotes
#   Description:    Generates a random quote.
#   Last Changed:   12/6/21
#   Changed By:     Denise Tanumihardja
#   Change Details: First implementation
# ================================================================
def rand_quotes():
    quotes = {
        "0": "'A ship does not sail with yesterday's winds.' -Louis L'Amour",
        "1": "'You can never cross the ocean until you have the courage to lose sight of the shore.' -Christopher Columbus",
        "2": "'Do not wait to strike till the iron is hot. Make it hot by striking.' -William Butler Yeats",
        "3": "'I’d rather attempt to do something great and fail, than to attempt nothing and succeed.' -Robert H. Schuller",
        "4": "'You don’t have to be great to start, but you have to start to be great.' -Zig Ziglar",
        "5": "'Research is what I’m doing when I don’t know what I’m doing.' -Wernher von Braun",
        "6": "'The secret of getting ahead is getting started.' -Mark Twain",
        "7": "'All our dreams can come true… if we have the courage to pursue them.' -Walt Disney",
        "8": "'In fact, the world needs more nerds.' -Ben Bernanke",
        "9": "'If we knew what we were doing, it would not be called research, would it?' -Albert Einstein",
        "10": "'Research means that you don’t know, but are willing to find out' -Charles F. Kettering",
        "11": "'Research is formalized curiosity. It is poking and prying with a purpose.' -Zora Neale Hurston",\
        "12": "'No research without action, no action without research' -Kurt Lewin",
        "13": "'I have not failed. I've just found 10,000 ways that won't work.' -Thomas A. Edison",
        "14": "'Let's go invent tomorrow instead of worrying about what happened yesterday.' -Steve Jobs",
        "15": "'Any sufficiently advanced technology is indistinguishable from magic.' -Arthur C. Clarke",
        "16": "'A man may die, nations may rise and fall, but an idea lives on.' -John F. Kennedy",
        "17": "'Only put off until tomorrow what you are willing to die having left undone.' -Pablo Picasso",
        "18": "'Without some goal and some efforts to reach it, no man can live.' -Fyodor Dostoyevsky",
        "19": "'A goal is a dream with a deadline.' -Napoleon Hill",
        "20": "'Remember to celebrate milestones as you prepare for the road ahead.' -Nelson Mandela",
        "21": "'All we have to do is decide what to do with the time that is given to us.' -Gandalf",
    }

    return quotes[str(random.randrange(22))]

# ================================================================
#   Name:           get_recommended_posts
#   Description:    Sorts posts for student to show those that
#                   best match their profile first.
#   Last Changed:   12/6/21
#   Changed By:     Reagan Kelley
#   Change Details: Revised to compensate for student major error
# ================================================================
def get_recommended_posts():
    if (current_user.get_user_type() == 'faculty'):
        return Post.query.order_by(Post.timestamp.desc()).all()
    
    # IF STUDENT: Implement Matchmaking algorthm
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    posts_with_major = []
    posts_with_fields = []
    posts_with_both = []
    matched_posts = []

    if(current_user.major is not None): # get all posts that match with student major
        student_major_id = Major.query.filter_by(id = current_user.major).first().id
        for post in posts:
            if(post.majors is not None):
                for major in post.majors:
                    if major.id == student_major_id:
                        posts_with_major.append(post)
    
    if(current_user.fields is not None): # get all posts that match with student's field list
        for field in current_user.fields:
            for post in posts:
                if (post.fields is not None):
                    for post_field in post.fields:
                        if field.id == post_field.id:
                            posts_with_fields.append(post)
        
    if len(posts_with_major) > 0: # get all posts that have student's major and desired fields
        for post in posts_with_major:
            if post in posts_with_fields:
                posts_with_both.append(post)

    for post in posts_with_both: # add posts with both first
        matched_posts.append(post)
    
    for post in posts_with_major: # add posts with major
        if (post in matched_posts) == False:
            matched_posts.append(post)

    for post in posts_with_fields: # add posts with fields
        if (post in matched_posts) == False:
            matched_posts.append(post)

    for post in posts: # add rest and put on bottom
        if (post in matched_posts) == False:
            matched_posts.append(post)

    return matched_posts


# ================================================================
#   Name:           Index Route
#   Description:    index route for basic flask implementation
#   Last Changed:   11/12/21
#   Changed By:     Reagan Kelley
#   Change Details: Added posts query to get all position posts :)
# ================================================================
@bp_routes.route('/', methods=['GET', 'POST'])
@bp_routes.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    num_collector.clear() # reset num_collector for later pages

    posts = get_recommended_posts()
    sform = SortForm()
    #print(current_user)
    if sform.validate_on_submit():
        if (sform.checkbox.data == True):
            posts = current_user.get_user_posts().all()
    return render_template('index.html', title="Lab Opportunities", posts=posts, post_count = len(posts), form= sform, quote = rand_quotes())

# ================================================================
#   Name:           Post Position Route
#   Description:    Post Position route for basic flask implementation
#   Last Changed:   12/3/21
#   Changed By:     Reagan Kelley
#   Change Details: Added dynamic form feature for fields
#                   Fixed bug
# ================================================================
@bp_routes.route('/postposition', methods=['GET', 'POST'])
@login_required
def postposition():
    if current_user.get_user_type() == 'student':
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))
    show_fields = False
    pForm = PostForm()


    if pForm.validate_on_submit():

        if(pForm.check.data):
  
            majors = pForm.majors.data
        
            num_collector.clear()
            for major in majors:
                num_collector.append(major.id)

            temp_title = pForm.title.data
            temp_body = pForm.body.data
            temp_majors = pForm.majors.data
            temp_time_commitment = pForm.time_commitment.data
            temp_start_date = pForm.start_date.data
            temp_end_date = pForm.end_date.data

            pForm = PostForm()
            pForm.title.data = temp_title
            pForm.body.data = temp_body
            pForm.majors.data = temp_majors
            pForm.time_commitment.data = temp_time_commitment
            pForm.start_date.data = temp_start_date
            pForm.end_date.data = temp_end_date
            print(pForm.fields.data)
            if(len(num_collector) == 0):
                show_fields = False
            else:
                show_fields = True
            return render_template('create.html', title="New Post", form = pForm, show_fields = show_fields)

        newPost = Post(user_id = current_user.id, 
                       title=pForm.title.data, 
                       body = pForm.body.data, 
                       majors = pForm.majors.data,
                       fields = pForm.fields.data, 
                       time_commitment = pForm.time_commitment.data,
                       start_date = pForm.start_date.data,
                       end_date = pForm.end_date.data)
        db.session.add(newPost)
        db.session.commit()
        flash('New Position Post "' + newPost.title + '" is on the Job Board!')
        return redirect(url_for('routes.index'))

    if(len(num_collector) == 0):
                show_fields = False
    else:
        show_fields = True
    return render_template('create.html', title="New Post", form = pForm, show_fields = show_fields)

# ================================================================
#   Name:           updateposition Route
#   Description:    The Page that allows a faculty to manage an existing
#                   post
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Restricted route
# ================================================================
@bp_routes.route('/updateposition/<post_id>', methods=['GET', 'POST'])
@login_required
def updateposition(post_id):
    post = Post.query.filter_by(id = post_id).first()

    if(post.user_id != current_user.id):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))

    if(post is None): #if post could not be found
        flash('Could not find this post.')
        return redirect(url_for('routes.index'))
    
    if (post.user_id != current_user.id): # if post does not belong to this user
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))
    
    pForm = PostForm()

    if request.method == 'GET': # Populate fields with existing data
        pForm.title.data = post.title
        pForm.body.data = post.body
        pForm.time_commitment.data = post.time_commitment
        pForm.start_date.data = post.start_date
        pForm.end_date.data = post.end_date
        pForm.majors.data = post.majors
        pForm.fields.data = post.fields

    if pForm.validate_on_submit():
        post.user_id = current_user.id
        post.title=pForm.title.data
        post.body = pForm.body.data 
        post.majors = pForm.majors.data
        post.fields = pForm.fields.data 
        post.time_commitment = pForm.time_commitment.data
        post.start_date = pForm.start_date.data
        post.end_date = pForm.end_date.data
        db.session.commit()
        flash('Post Edit Successful')
        return redirect(url_for('routes.index'))

    return render_template('updateposition.html', title="Update Post", post = post, form = pForm)
    
# ================================================================
#   Name:           Delete Post
#   Description:    Deletes an existing post
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Restrited route
# ================================================================
@bp_routes.route('/delete_post/<post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id = post_id).first()
    
    if(post.user_id != current_user.id):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))

    if(post is None): #if post could not be found
        flash('Could not find this post.')
        return redirect(url_for('routes.index'))
    
    if (post.user_id != current_user.id): # if post does not belong to this user
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))

    applications = post.get_applicants()

    for application in applications: # Remove connection in applications
        application.phantom_name = post.title
        application.make_phantom()  # Retain post information

    db.session.delete(post)
    db.session.commit()
    #flash('Deleted Post [' + post.title + ']')
    return redirect(url_for('routes.index'))


# ================================================================
#   Name:           Student Profile Update Route
#   Description:    Updates the student profile with inputed information
#   Last Changed:   11/14/21
#   Changed By:     Denise Tanumihardja
#   Change Details: Initial Implementation
# ================================================================
@bp_routes.route('/student_profile', methods=['GET'])
@login_required
def student_profile():
    if(current_user.get_user_type() == 'faculty'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))

    return render_template('profile.html', title="Student Profile", profile = current_user)


# ================================================================
#   Name:           Student Profile Update Route
#   Description:    Updates the student profile with input information
#   Last Changed:   12/6/21
#   Changed By:     Reagan Kelley
#   Change Details: Revised to compensate for student major error
# ================================================================
@bp_routes.route('/student_profile_update', methods=['GET', 'POST'])
@login_required
def update_student_profile():
    if(current_user.get_user_type() == 'Faculty'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))
    proForm = ProfileForm()
   
    num_collector.clear()
    majors = Major.query.all()
    for major in majors:
        if major.id != -1:
            num_collector.append(major.id)
    
    if request.method == 'GET': # Populate fields with existing data
        proForm.first_name.data = current_user.first_name
        proForm.last_name.data = current_user.last_name
        proForm.wsu_id.data = current_user.wsu_id
        proForm.phone_no.data = current_user.phone_no
        proForm.gpa.data = current_user.gpa
        proForm.expected_grad_date.data = current_user.expected_grad_date
        proForm.elect_courses.data = current_user.elect_courses
        proForm.languages.data = current_user.languages
        proForm.prior_research.data = current_user.prior_research

        proForm.major.data = Major.query.filter_by(id = current_user.major).first()
        proForm.fields.data = current_user.fields


    if proForm.validate_on_submit():
        
        major_name = Major.query.filter_by(id = (proForm.major.data).id).first()

        # update current user with form info
        current_user.wsu_id = proForm.wsu_id.data
        current_user.first_name = proForm.first_name.data
        current_user.last_name = proForm.last_name.data
        current_user.phone_no = proForm.phone_no.data
        current_user.major = major_name.id
        current_user.fields = proForm.fields.data
        current_user.gpa = proForm.gpa.data
        current_user.expected_grad_date = proForm.expected_grad_date.data
        current_user.elect_courses = proForm.elect_courses.data
        ##current_user.research_topics = research_tags.get_research_field()
        current_user.languages = proForm.languages.data
        current_user.prior_research = proForm.prior_research.data

        # commit changes
        db.session.commit()
        flash('Profile Successfully Updated!')
        return redirect(url_for('routes.student_profile'))
    return render_template('updateprofile.html', title = "Student Profile", update = proForm, user = current_user)

# ================================================================
#   Name:           Apply Route
#   Description:    Backend route to apply to position post
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Restricted route
# ================================================================
@bp_routes.route('/apply/<postid>/<brief>/<ref>', methods = ['GET', 'POST'])
@login_required
def apply(postid, brief, ref):

    if(current_user.get_user_type() == 'faculty'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))

    thepost = Post.query.filter_by(id = postid).first()
    if thepost is None:
        flash('Class with id "{}" not found.'.format(postid))
        return redirect(url_for('routes.index'))
    current_user.apply(thepost, brief, ref)
    db.session.commit()
    flash('You applied for: {}!'.format(thepost.title))
    return redirect(url_for('routes.index'))

# ================================================================
#   Name:           Unapply Route
#   Description:    Backend route to unapply to position post
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Restricted route
# ================================================================
@bp_routes.route('/unapply/<postid>', methods = ['POST'])
@login_required
def unapply(postid):

    if(current_user.get_user_type() == 'faculty'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))

    thepost = Post.query.filter_by(id = postid).first()
    if thepost is None:
        flash('Class with id "{}" not found.'.format(postid))
        return redirect(url_for('routes.index'))
    current_user.unapply(thepost)
    db.session.commit()
    flash('You redrew your application for: {}!'.format(thepost.title))
    return redirect(url_for('routes.index'))

# ================================================================
#   Name:           Submit Application Route
#   Description:    Form Page students are directed to when they 
#                   want to apply to a postion post.
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Revised to compensate for new database model
# ================================================================
@bp_routes.route('/submit_application/<postid>', methods = ['GET', 'POST'])
@login_required
def submit_application(postid):
    if(current_user.get_user_type() == 'faculty'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))
    
    thepost = Post.query.filter_by(id = postid).first()
    aForm = ApplicationForm()

    if aForm.validate_on_submit():
        return redirect(url_for('routes.apply', postid = postid, brief = aForm.personal_statement.data, ref = aForm.faculty_ref_name.data))

    return render_template('submit.html', title="Apply for Position", post = thepost, form = aForm, profile = current_user)

# ================================================================
#   Name:           Applications Route
#   Description:    Prints all applications for faculty postion posts
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Restricted routes
# ================================================================
@bp_routes.route('/applications', methods=['GET', 'POST'])
@login_required
def applications():
    num_collector.clear() # reset num_collector for later pages
    if(current_user.get_user_type() == 'faculty'):
        posts = current_user.get_user_posts()
        page_title = "Applications"
    else: # current user is student
        post_id_list = []
        page_title = "My Applications"
        # get all post id's for posts student has applied to
        for application in current_user.applications:
            post_id_list.append(application.post_id)
        posts = db.session.query(Post).filter(Post.id.in_(n for n in post_id_list))

    print(posts.count())
    return render_template('applications.html', title=page_title, posts = posts)

# ================================================================
#   Name:           Review Route
#   Description:    Displays application of desired student who 
#                   applied to the faculty's position post.
#   Last Changed:   12/5/21
#   Changed By:     Reagan Kelley
#   Change Details: Restricted route
# ================================================================
@bp_routes.route('/review/<postid>/<userid>', methods = ['GET', 'POST'])
@login_required
def review(postid, userid):

    thepost = Post.query.filter_by(id = postid).first()
    if(thepost.writer.id != current_user.id):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))

    application = Application.query.filter_by(applicant_id = userid, post_id = postid).first()
    return render_template('review.html', title="Review Application", application = application)

# ================================================================
#   Name:           Update Route
#   Description:    Backend route that changes 
#                   the status of an application
#   Last Changed:   11/16/21
#   Changed By:     Reagan Kelley
#   Change Details: Initial Implementation
# ================================================================
@bp_routes.route('/update/<postid>/<userid>/<change>', methods = ['GET', 'POST'])
@login_required
def update(postid, userid, change):
    thepost = Post.query.filter_by(id = postid).first()
    if(thepost.writer.id != current_user.id):
        flash('You do not have permission to access this page.')
        return redirect(url_for('routes.index'))

    application = Application.query.filter_by(applicant_id = userid, post_id = postid).first()

    if change == 'Interview':
        application.status = 'Interview'
    elif (change == 'Reject'):
        application.status = 'Reject'
    elif (change == 'Hired'):
        application.status = 'Hired'
    
    db.session.commit()

    return redirect(url_for('routes.applications'))



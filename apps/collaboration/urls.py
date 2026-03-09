from django.urls import path
from . import views

app_name = 'collaboration'

urlpatterns = [
    path('', views.CollaborationIndexView.as_view(), name='index'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('project/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('submit/', views.CollaborationSubmissionView.as_view(), name='submit'),
    path('submit/success/', views.SubmissionSuccessView.as_view(), name='submission_success'),
    path('propose/', views.ProjectProposalView.as_view(), name='propose'),
    path('propose/success/', views.ProposalSuccessView.as_view(), name='proposal_success'),
    path('collaborators/', views.CollaboratorsListView.as_view(), name='collaborators'),
]

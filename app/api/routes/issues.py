import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.agent.core import AgentService
from app.api.Database import init_db, get_db
from app.api.models import Issue
from app.api.schemas import IssueUpdate, IssueCreate, IssueResponse

# from app.storage import load_data,save_data
router = APIRouter(prefix="/api/issues" ,tags=["Issues"])

agent = AgentService()

@router.on_event("startup")
def startup_event():
    init_db()

@router.post("/issues", status_code=status.HTTP_201_CREATED, response_model=IssueResponse)
def create_issue(query:str,db:Session = Depends(get_db)):
    """
    Create an issue using natural language query.

    Args:
        query: Natural language description (e.g., "Website giving 502 error, high priority")
        db: Database session

    Returns:
        Created issue object
    """

    try:
        agent_response = agent.process_chat(
            user_input=query,
            chat_history=[]
        )

        if not agent_response.get("tool_result"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract issue details from query. Please be more specific."
            )
        issue_data = json.loads(agent_response["tool_result"])

        issue = IssueCreate(**issue_data)

        db_issue = Issue(**issue.dict())
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)

        return db_issue

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid issue data format from agent"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating issue: {str(e)}"
        )




    pass

@router.get("/issues", response_model=List[IssueResponse])
def get_issues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    issues = db.query(Issue).offset(skip).limit(limit).all()
    return issues


@router.put("/issue/", response_model=IssueResponse)
def update_issue( query: str,db: Session = Depends(get_db)):
    """
    Update an issue using natural language.

    Examples:
        - "Change priority to high"
        - "Update status to in_progress"
        - "Mark as closed"
    """
    # issue_id: str, issue_update: IssueUpdate,
    try :
        agent_response= agent.process_chat(user_input=query,chat_history=[])

        if not agent_response.get("tool_result"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent did not return update data."
            )

        issue_data = json.loads(agent_response["tool_result"])
        db_issue = db.query(Issue).filter(Issue.issue_id == issue_data["issue_id"]).first()
        if not db_issue:
            raise HTTPException(status_code=404, detail="Issue not found")
        update_data = issue_data["updates"]
        print(update_data)
        for field, value in update_data.items():
            setattr(db_issue, field, value)
        db_issue.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_issue)
        return db_issue
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid issue data format from agent"
        )



    # if not db_issue:
    #     raise HTTPException(status_code=404, detail="Issue not found")
    #
    # # Update only provided fields
    # update_data = issue_update.dict(exclude_unset=True)
    # for field, value in update_data.items():
    #     setattr(db_issue, field, value)
    #
    # db_issue.updated_at = datetime.utcnow()
    # db.commit()
    # db.refresh(db_issue)
    # return db_issue


# Delete issue
@router.delete("/issues/{issue_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_uuid: str, db: Session = Depends(get_db)):
    db_issue = db.query(Issue).filter(Issue.uuid == issue_uuid).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(db_issue)
    db.commit()
    return None

@router.get("/issue/{issue_id}",status_code=status.HTTP_200_OK,response_model=IssueResponse)
def get_issue(issue_uuid: str, db: Session = Depends(get_db)):
    db_issue = db.query(Issue).filter(Issue.uuid == issue_uuid).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    return db_issue

@router.get("/")
def health_check():
    return {"status": "healthy", "message": "Issue Tracker API is running"}


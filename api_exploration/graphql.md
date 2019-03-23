# GraphQl


## Detect types
{
  __schema {
    queryType {
      name
    }
  }
}

```
{
  "data": {
    "__schema": {
      "types": [
        {
          "name": "Query"
        },
        {
          "name": "User"
        },
        {
          "name": "Node"
        },
        {
          "name": "ID"
        },
        {
          "name": "UniformResourceLocatable"
        },
        {
          "name": "URI"
        },
        {
          "name": "String"
        },
        {
          "name": "Boolean"
        },
        {
          "name": "Int"
        },
        {
          "name": "ProjectOrder"
        },
        {
          "name": "ProjectOrderField"
        },
        {
          "name": "OrderDirection"
        },
        {
          "name": "ProjectConnection"
        },
        {
          "name": "PageInfo"
        },
        {
          "name": "ProjectEdge"
        },
        {
          "name": "Project"
        },
        {
          "name": "VoteConnection"
        },
        {
          "name": "VoteEdge"
        },
        {
          "name": "Vote"
        },
        {
          "name": "DateTime"
        },
        {
          "name": "UserConnection"
        },
        {
          "name": "UserEdge"
        },
        {
          "name": "EventConnection"
        },
        {
          "name": "EventEdge"
        },
        {
          "name": "Event"
        },
        {
          "name": "HTML"
        },
        {
          "name": "Float"
        },
        {
          "name": "__Schema"
        },
        {
          "name": "__Type"
        },
        {
          "name": "__TypeKind"
        },
        {
          "name": "__Field"
        },
        {
          "name": "__InputValue"
        },
        {
          "name": "__EnumValue"
        },
        {
          "name": "__Directive"
        },
        {
          "name": "__DirectiveLocation"
        },
        {
          "name": "Consultation"
        },
        {
          "name": "Questionnaire"
        },
        {
          "name": "ProposalVote"
        },
        {
          "name": "Publishable"
        },
        {
          "name": "NotPublishedReason"
        },
        {
          "name": "PrivatableVote"
        },
        {
          "name": "Proposal"
        },
        {
          "name": "Trashable"
        },
        {
          "name": "TrashableStatus"
        },
        {
          "name": "Response"
        },
        {
          "name": "Question"
        },
        {
          "name": "ValueResponse"
        },
        {
          "name": "CollectStep"
        },
        {
          "name": "ProposalOrder"
        },
        {
          "name": "ProposalOrderField"
        },
        {
          "name": "ProposalConnection"
        },
        {
          "name": "ProposalEdge"
        },
        {
          "name": "SimpleQuestion"
        }
      ]
    }
  }
}
```
## More information on 1 type

{
  __type(name: "Query") {
    name
  }
}


{
  __type(name: "Proposal") {
    name
    fields {
      name
      type {
        name
        kind
      }
    }
  }
}

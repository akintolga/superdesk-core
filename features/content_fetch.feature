Feature: Fetch Items from Ingest

    @auth
    @provider
    Scenario: Fetch an item and validate metadata set by API
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E", "byline": "Chuck Norris", "dateline": {"source": "Reuters"}}]
      """
      When we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get new resource
      When we get "/archive?q=#desks._id#"
      Then we get list with 1 items
      """
      {"_items": [
      	{
      		"family_id": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E",
      		"ingest_id": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E",
      		"operation": "fetch",
      		"sign_off": "abc",
      		"byline": "Chuck Norris",
      		"dateline": {"source": "Reuters"}
      	}
      ]}
      """


    @auth
    @provider
    Scenario: Fetch an item empty byline and dateline doesn't get populated
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}]
      """
      When we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get new resource
      When we get "/archive?q=#desks._id#"
      Then we get no "byline"
      Then we get no "dateline"


    @auth
    @provider
    Scenario: Fetch an item of type Media and validate metadata set by API
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      When we fetch from "reuters" ingest "tag_reuters.com_0000_newsml_GM1EA7M13RP01:484616934"
      And we post to "/ingest/#reuters.tag_reuters.com_0000_newsml_GM1EA7M13RP01:484616934#/fetch" with success
      """
      {
      "desk": "#desks._id#"
      }
      """
      Then we get "_id"
      When we get "/archive/#_id#"
      Then we get existing resource
      """
      {   "sign_off": "abc",
          "renditions": {
              "baseImage": {"height": 845, "mimetype": "image/jpeg", "width": 1400},
              "original": {"height": 2113, "mimetype": "image/jpeg", "width": 3500},
              "thumbnail": {"height": 120, "mimetype": "image/jpeg", "width": 198},
              "viewImage": {"height": 386, "mimetype": "image/jpeg", "width": 640}
          }
      }
      """

    @auth
    @provider
    @test
    Scenario: Fetch a package and validate metadata set by API
      Given empty "ingest"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_KBN0FL0NM:10"
      And we post to "/ingest/#reuters.tag_reuters.com_2014_newsml_KBN0FL0NM:10#/fetch"
      """
      {
      "desk": "#desks._id#"
      }
      """
      And we get "archive"
      Then we get existing resource
      """
      {
          "_items": [
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "picture",
                  "sign_off": "abc"
              },
              {
                  "_current_version": 1,
                  "groups": [
                      {
                          "refs": [
                              {"itemClass": "icls:text"},
                              {"itemClass": "icls:picture"},
                              {"itemClass": "icls:picture"},
                              {"itemClass": "icls:picture"}
                          ]
                      },
                      {"refs": [{"itemClass": "icls:text"}]}
                  ],
                  "state": "fetched",
                  "type": "composite",
                  "sign_off": "abc"
              },
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "picture",
                  "sign_off": "abc"
              },
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "text",
                  "sign_off": "abc"
              },
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "picture",
                  "sign_off": "abc"
              },
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "text",
                  "sign_off": "abc"
              }
          ]
      }
      """

    @auth
    @provider
    Scenario: Fetch same ingest item to a desk twice
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}]
      """
      When we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      And we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get new resource
      When we get "/archive?q=#desks._id#"
      Then we get list with 2 items
      """
      {"_items": [
              {
                "family_id": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E",
                "unique_id": 1
               },
              {
                "family_id": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E",
                "unique_id": 2
              }
              ]}
      """

    @auth
    Scenario: Fetch should fail when invalid ingest id is passed
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And empty "ingest"
      When we post to "/ingest/invalid_id/fetch"
      """
      {
      "desk": "#desks._id#"
      }
      """
      Then we get error 404
      """
      {"_message": "Fail to found ingest item with _id: invalid_id", "_status": "ERR"}
      """

    @auth
    @provider
    Scenario: Fetch should fail when no desk is specified
      Given empty "archive"
      When we fetch from "reuters" ingest "tag_reuters.com_0000_newsml_GM1EA7M13RP01:484616934"
      When we post to "/ingest/tag_reuters.com_0000_newsml_GM1EA7M13RP01:484616934/fetch"
      """
      {}
      """
      Then we get error 400
      """
      {"_issues": {"desk": {"required": 1}}}
      """

    @auth
    @provider
    Scenario: Fetched item should have "in_progress" state when locked and edited
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}]
      """
      When we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get "_id"
      When we post to "/archive/#_id#/lock"
      """
      {}
      """
      And we patch "/archive/#_id#"
      """
      {"headline": "test 2"}
      """
      Then we get existing resource
      """
      {"headline": "test 2", "state": "in_progress", "task": {"desk": "#desks._id#"}}
      """

    @auth
    @provider
    Scenario: User can't fetch content without a privilege
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}]
      """
      When we login as user "foo" with password "bar" and user type "user"
      """
      {"user_type": "user", "email": "foo.bar@foobar.org"}
      """
      And we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get response code 403

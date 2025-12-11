"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const cdk = require("aws-cdk-lib");
test('SQS Queue and SNS Topic Created', () => {
    const app = new cdk.App();
    // WHEN
    //const stack = new CdkCode.CdkCodeStack(app, 'MyTestStack');
    // THEN
    //  const template = Template.fromStack(stack);
    //  template.hasResourceProperties('AWS::SQS::Queue', {
    //    VisibilityTimeout: 300
    //  });
    //  template.resourceCountIs('AWS::SNS::Topic', 1);
});
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiY2RrLWNvZGUudGVzdC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbImNkay1jb2RlLnRlc3QudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7QUFBQSxtQ0FBbUM7QUFJbkMsSUFBSSxDQUFDLGlDQUFpQyxFQUFFLEdBQUcsRUFBRTtJQUMzQyxNQUFNLEdBQUcsR0FBRyxJQUFJLEdBQUcsQ0FBQyxHQUFHLEVBQUUsQ0FBQztJQUMxQixPQUFPO0lBQ1AsNkRBQTZEO0lBQzdELE9BQU87SUFFVCwrQ0FBK0M7SUFFL0MsdURBQXVEO0lBQ3ZELDRCQUE0QjtJQUM1QixPQUFPO0lBQ1AsbURBQW1EO0FBQ25ELENBQUMsQ0FBQyxDQUFDIiwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0ICogYXMgY2RrIGZyb20gJ2F3cy1jZGstbGliJztcclxuaW1wb3J0IHsgVGVtcGxhdGUsIE1hdGNoIH0gZnJvbSAnYXdzLWNkay1saWIvYXNzZXJ0aW9ucyc7XHJcbmltcG9ydCAqIGFzIENka0NvZGUgZnJvbSAnLi4vbGliL2Nkay1jb2RlLXN0YWNrJztcclxuXHJcbnRlc3QoJ1NRUyBRdWV1ZSBhbmQgU05TIFRvcGljIENyZWF0ZWQnLCAoKSA9PiB7XHJcbiAgY29uc3QgYXBwID0gbmV3IGNkay5BcHAoKTtcclxuICAvLyBXSEVOXHJcbiAgLy9jb25zdCBzdGFjayA9IG5ldyBDZGtDb2RlLkNka0NvZGVTdGFjayhhcHAsICdNeVRlc3RTdGFjaycpO1xyXG4gIC8vIFRIRU5cclxuXHJcbi8vICBjb25zdCB0ZW1wbGF0ZSA9IFRlbXBsYXRlLmZyb21TdGFjayhzdGFjayk7XHJcblxyXG4vLyAgdGVtcGxhdGUuaGFzUmVzb3VyY2VQcm9wZXJ0aWVzKCdBV1M6OlNRUzo6UXVldWUnLCB7XHJcbi8vICAgIFZpc2liaWxpdHlUaW1lb3V0OiAzMDBcclxuLy8gIH0pO1xyXG4vLyAgdGVtcGxhdGUucmVzb3VyY2VDb3VudElzKCdBV1M6OlNOUzo6VG9waWMnLCAxKTtcclxufSk7XHJcbiJdfQ==
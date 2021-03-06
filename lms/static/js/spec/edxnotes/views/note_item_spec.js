define([
    'jquery', 'underscore', 'js/common_helpers/ajax_helpers',
    'js/common_helpers/template_helpers', 'js/spec/edxnotes/helpers', 'logger',
    'js/edxnotes/models/note', 'js/edxnotes/views/note_item',
    'js/spec/edxnotes/custom_matchers'
], function(
    $, _, AjaxHelpers, TemplateHelpers, Helpers, Logger, NoteModel, NoteItemView,
    customMatchers
) {
    'use strict';
    describe('EdxNotes NoteItemView', function() {
        var getView = function (model) {
            model = new NoteModel(_.defaults(model || {}, {
                id: 'id-123',
                user: 'user-123',
                usage_id: 'usage_id-123',
                created: 'December 11, 2014 at 11:12AM',
                updated: 'December 11, 2014 at 11:12AM',
                text: 'Third added model',
                quote: Helpers.LONG_TEXT,
                unit: {
                    url: 'http://example.com/'
                }
            }));

            return new NoteItemView({model: model}).render();
        };

        beforeEach(function() {
            customMatchers(this);
            TemplateHelpers.installTemplate('templates/edxnotes/note-item');
            spyOn(Logger, 'log').andCallThrough();
        });

        it('can be rendered properly', function() {
            var view = getView(),
                unitLink = view.$('.reference-unit-link').get(0);

            expect(view.$el).toContain('.note-excerpt-more-link');
            expect(view.$el).toContainText(Helpers.PRUNED_TEXT);
            expect(view.$el).toContainText('More');
            view.$('.note-excerpt-more-link').click();

            expect(view.$el).toContainText(Helpers.LONG_TEXT);
            expect(view.$el).toContainText('Less');

            view = getView({quote: Helpers.SHORT_TEXT});
            expect(view.$el).not.toContain('.note-excerpt-more-link');
            expect(view.$el).toContainText(Helpers.SHORT_TEXT);

            expect(unitLink.hash).toBe('#id-123');
        });

        it('should display update value and accompanying text', function() {
            var view = getView();
            expect(view.$('.reference-title')[1]).toContainText('Last Edited:');
            expect(view.$('.reference-updated-date').last()).toContainText('December 11, 2014 at 11:12AM');
        });

        it('should not display tags if there are none', function() {
            var view = getView();
            expect(view.$el).not.toContain('.reference-tags');
            expect(view.$('.reference-title').length).toBe(2);
        });

        it('should display tags if they exist', function() {
            var view = getView({tags: ["First", "Second"]});
            expect(view.$('.reference-title').length).toBe(3);
            expect(view.$('.reference-title')[2]).toContainText('Tags:');
            expect(view.$('.reference-tags').last()).toContainText('First, Second');
        });

        it('should log the edx.student_notes.used_unit_link event properly', function () {
            var requests = AjaxHelpers.requests(this),
                view = getView();
            spyOn(view, 'redirectTo');
            view.$('.reference-unit-link').click();
            expect(Logger.log).toHaveBeenCalledWith(
                'edx.student_notes.used_unit_link',
                {
                    'note_id': 'id-123',
                    'component_usage_id': 'usage_id-123'
                },
                null,
                {
                    'timeout': 2000
                }
            );
            expect(view.redirectTo).not.toHaveBeenCalled();
            AjaxHelpers.respondWithJson(requests, {});
            expect(view.redirectTo).toHaveBeenCalledWith('http://example.com/#id-123');
        });
    });
});
